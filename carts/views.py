from django.shortcuts import render, redirect, get_object_or_404

from store.models import Product, Variation

from .models import Cart, CartItem

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

from . import views


from django.http import HttpResponse


# Create your views here.


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    
    # get current user
    current_user = request.user
    
    print('Current User -> ', current_user
          )
    product = Product.objects.get(id=product_id)

    print('***** before user authentication check *****')
    print('Product -> ', product)
    
    
    # check if user is authenticated
    
    if current_user.is_authenticated:
        
        # contains product variation list
        product_variation = []    
        
        if request.method == 'POST':
            
            for item in request.POST:
                key = item 
                value = request.POST[key]
        
                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                    print('Looping through Product Variations ->' ,variation)
                except:
                    pass
        
        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists()
        
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, user=current_user)
            
            # if current variation is in the existing variation then add count
            ex_var_list = []
            id = []
            
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
                    
            print('printing ex_var_list ', ex_var_list)
            print('printing product_variation'  , product_variation)
            
            # ---------------------------------------------
            # if product variation is in current list
            # ---------------------------------------------#
            if product_variation in ex_var_list:
                # increase cart item quantity

                index = ex_var_list.index(product_variation)
                print('index' , index)
                print('product variation', product_variation)
                print()
                
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()
                print('Existing Item/Variation Added', product_variation)
                print()
                
            else:
                # create a new cart item
                item = CartItem.objects.create(product=product, quantity=1, user=current_user)

                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
                print('Existing Cart Item - New Variation Added ... ', product_variation)
        else:
            # create new cart item
            
            print('Create new cart item - before item creation...'  )
            
            cart_item = CartItem.objects.create(product = product, quantity = 1, cart = current_user)
            
            print('New Cart Item -> ', str(cart_item ))
            
            print('New Cart Item Variations -> ', cart_item.variations)
            
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)

            cart_item.save()
            
        return redirect('cart')
    
    else:
        # if user is not authenticated
        # contains product variation list
        product_variation = []    
        
        if request.method == 'POST':
            
            for item in request.POST:
                key = item 
                value = request.POST[key]
        
                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                    print('Looping through Product Variations ->' ,variation)
                except:
                    pass
        
        # getting the cart id               
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )        
        cart.save()
        
        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
        
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, cart=cart)
            
            # exiting_variations 
            # current variation 
            # item_id -> from database
            
            # if current variation is in the existing variation then add count
            ex_var_list = []
            id = []
            
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
                    
            print('printing ex_var_list ', ex_var_list)
            print('printing product_variation'  , product_variation)
            
            # ---------------------------------------------
            # if product variation is in current list
            # ---------------------------------------------#
            if product_variation in ex_var_list:
                # increase cart item quantity

                index = ex_var_list.index(product_variation)
                print('index' , index)
                print('product variation', product_variation)
                print()
                
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()
                print('Existing Item/Variation Added', product_variation)
                print()
                
            else:
                # create a new cart item
                item = CartItem.objects.create(product=product, quantity=1, cart=cart)

                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
                print('Existing Cart Item - New Variation Added ... ', product_variation)
        else:
            # create new cart item
            cart_item = CartItem.objects.create(
                product = product, 
                quantity = 1,
                cart = cart,
            )
            
            print('New Cart Item -> ', str(cart_item ))
            
            print('New Cart Item Variations -> ', cart_item.variations)
            
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)

            cart_item.save()
            
        return redirect('cart')
        
        
def remove_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
            
        if cart_item.quantity > 1:
            cart_item.quantity -= 1  
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')


def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
          cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)    
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    
    cart_item.delete()
    return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):

    try:
        tax = 0 
        grand_total = 0
        
        if request.user.is_authenticated:
            # get cart items for logged in user
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            # if user is not authenticated
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
            
        tax = (8 * total) / 100
        grand_total = total + tax
            
    except ObjectDoesNotExist:
        pass
    
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
        
    }
    
    return render(request, 'store/cart.html', context)


@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0 
        grand_total = 0
        
        if request.user.is_authenticated:
            # get cart items for logged in user
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            # if user is not authenticated
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
            
        
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (8 * total) / 100
        grand_total = total + tax
            
    except ObjectDoesNotExist:
        pass
    
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
        
    }
    return render(request, 'store/checkout.html', context)




