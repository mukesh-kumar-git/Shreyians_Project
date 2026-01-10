from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.text import slugify
from .models import Course, Cart, CartItem
from django.contrib.auth.models import User

CustomUser = get_user_model()


# ===================== SIGNUP =====================
def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('signup')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect('signup')

        CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, "Account created successfully. Please sign in.")
        return redirect('signin')

    return render(request, 'signup.html')


# ===================== SIGNIN =====================
def signin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            username = User.objects.get(email=email).username
        except User.DoesNotExist:
            messages.error(request, "Email not registered")
            return render(request, 'signin.html')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid email or password")

    return render(request, 'signin.html')



# ===================== SIGNOUT =====================
def signout(request):
    logout(request)
    return redirect('signin')


# ===================== HOME =====================
def home(request):
    courses = Course.objects.all()
    return render(request, "home.html", {"courses": courses})


# ===================== COURSE LIST =====================
def course_list(request):
    courses = Course.objects.all()
    return render(request, "courses.html", {"courses": courses})


# ===================== COURSE DETAIL =====================
def course_detail(request, slug):
    course = Course.objects.filter(slug=slug).first()
    if not course:
        return redirect('course_list')
    return render(request, "course_detail.html", {"course": course})


# ===================== ADD COURSE =====================
def add_course(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        short_description = request.POST.get('short_description')
        full_description = request.POST.get('full_description')
        price_original = request.POST.get('price_original')
        price_discounted = request.POST.get('price_discounted')
        discount_percentage = request.POST.get('discount_percentage')
        language = request.POST.get('language')
        schedule = request.POST.get('schedule')
        course_validity = request.POST.get('course_validity')
        image = request.FILES.get('image')

        base_slug = slugify(title)
        slug = base_slug
        i = 1
        while Course.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{i}"
            i += 1

        Course.objects.create(
            title=title,
            slug=slug,
            short_description=short_description,
            full_description=full_description,
            price_original=price_original,
            price_discounted=price_discounted,
            discount_percentage=discount_percentage,
            language=language,
            schedule=schedule,
            course_validity=course_validity,
            image=image
        )

        messages.success(request, "Course added successfully")
        return redirect('home')

    return render(request, 'add_course.html')


# ===================== ADD TO CART =====================
def add_to_cart(request, course_id):
    course = Course.objects.filter(id=course_id).first()
    if not course:
        return redirect('course_list')

    # ---------- LOGGED IN USER ----------
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)

        item, created = CartItem.objects.get_or_create(cart=cart, course=course)
        if not created:
            item.quantity += 1
        item.save()

        # merge session cart
        session_cart = request.session.get('cart')
        if session_cart:
            for cid, qty in session_cart.items():
                c = Course.objects.filter(id=cid).first()
                if not c:
                    continue
                i, created = CartItem.objects.get_or_create(cart=cart, course=c)
                if not created:
                    i.quantity += qty
                else:
                    i.quantity = qty
                i.save()
            del request.session['cart']

        return redirect('cart_page')

    # ---------- SESSION CART ----------
    cart = request.session.get('cart', {})
    cid = str(course.id)

    if cid in cart:
        cart[cid] += 1
    else:
        cart[cid] = 1

    request.session['cart'] = cart
    request.session.modified = True
    return redirect('cart_page')


# ===================== CART PAGE =====================
def cart_page(request):
    cart_items = []
    total_items = 0
    total_price = 0

    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            for item in CartItem.objects.filter(cart=cart):
                price = item.course.price_discounted or 0
                subtotal = price * item.quantity
                cart_items.append({
                    "course": item.course,
                    "quantity": item.quantity,
                    "price": price,
                    "subtotal": subtotal
                })
                total_items += item.quantity
                total_price += subtotal
    else:
        session_cart = request.session.get('cart', {})
        for cid, qty in session_cart.items():
            course = Course.objects.filter(id=cid).first()
            if not course:
                continue
            price = course.price_discounted or 0
            subtotal = price * qty
            cart_items.append({
                "course": course,
                "quantity": qty,
                "price": price,
                "subtotal": subtotal
            })
            total_items += qty
            total_price += subtotal

    return render(request, "cart.html", {
        "cart_items": cart_items,
        "total_items": total_items,
        "total_price": total_price
    })


# ===================== UPDATE CART =====================
def update_cart(request, course_id, action):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if not cart:
            return redirect('cart_page')

        item = CartItem.objects.filter(cart=cart, course_id=course_id).first()
        if not item:
            return redirect('cart_page')

        if action == 'inc':
            item.quantity += 1
        elif action == 'dec':
            if item.quantity > 1:
                item.quantity -= 1
            else:
                item.delete()
                return redirect('cart_page')
        elif action == 'remove':
            item.delete()
            return redirect('cart_page')

        item.save()
    else:
        cart = request.session.get('cart', {})
        cid = str(course_id)

        if action == 'inc':
            cart[cid] += 1
        elif action == 'dec':
            if cart[cid] > 1:
                cart[cid] -= 1
            else:
                del cart[cid]
        elif action == 'remove':
            del cart[cid]

        request.session['cart'] = cart
        request.session.modified = True

    return redirect('cart_page')


# ===================== CHECKOUT =====================
def checkout_page(request):
    cart_items = []
    total_items = 0
    total_price = 0

    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            for item in CartItem.objects.filter(cart=cart):
                price = item.course.price_discounted or 0
                subtotal = price * item.quantity
                cart_items.append({
                    "course": item.course,
                    "quantity": item.quantity,
                    "price": price,
                    "subtotal": subtotal
                })
                total_items += item.quantity
                total_price += subtotal
    else:
        session_cart = request.session.get('cart', {})
        for cid, qty in session_cart.items():
            course = Course.objects.filter(id=cid).first()
            if not course:
                continue
            price = course.price_discounted or 0
            subtotal = price * qty
            cart_items.append({
                "course": course,
                "quantity": qty,
                "price": price,
                "subtotal": subtotal
            })
            total_items += qty
            total_price += subtotal

    return render(request, "checkout.html", {
        "cart_items": cart_items,
        "total_items": total_items,
        "total_price": total_price
    })


# ===================== ORDER CONFIRM =====================
@login_required(login_url='signin')
def confirm_order(request):
    cart = Cart.objects.filter(user=request.user).first()
    if cart:
        cart.cartitem_set.all().delete()
    return render(request, "order_success.html")