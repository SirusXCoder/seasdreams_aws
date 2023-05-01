
from .models import Cart, CartItem
from .views import _cart_id



def counter(request):
    cart_count = 0
    if 'admin' in request.path:
        return {}
    else:
        # 
        try: 
            cart = Cart.objects.filter(cart_id=_cart_id(request))
            
            # check to see if user is logged in and get count for current user
            if request.user.is_authenticated:
                # get cart items for logged in user
                cart_items = CartItem.objects.all().filter(user=request.user)
            else:
                # get cart items if no user is authenticated     
                cart_items = CartItem.objects.all().filter(cart=cart[:1])
            for cart_item in cart_items:
                cart_count += cart_item.quantity
        except Cart.DoesNotExist:
            cart_count = 0
        
        return dict(cart_count=cart_count)
    
    
    