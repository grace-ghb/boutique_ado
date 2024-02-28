from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.db.models.functions import Lower
from .models import Product, Category

# Create your views here.

def all_products(request):
    """ A view to show all products, including sorting and search queries """

    products = Product.objects.all()    # Retrieve all products from the db
    query = None    # Initialize variable
    categories = None
    sort = None
    direction = None

    if request.GET:
        if 'sort' in request.GET:
            # If 'sort' is present in the req
            # it sets the sorting key('sortkey') based on user's choice
            sortkey = request.GET['sort']
            sort = sortkey
            if sortkey == 'name':
                # Sorting by name, it annottates the queryset with a lowercase
                # version of the name
                sortkey = 'lower_name'
                products = products.annotate(lower_name=Lower('name'))
            if sortkey == 'category':
                # It's also handle sorting by category                
                sortkey = 'category__name'            
            if 'direction' in request.GET:
                # If 'direction' is present, it adjust the sorting key
                # for asc or desc order 
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            products = products.order_by(sortkey) # Apply sorting to the queryset

        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            # It filters the products based on the specified categories
            products = products.filter(category__name__in=categories)
            # It also retrieves the corresponding category object
            categories = Category.objects.filter(name__in=categories)

        if 'q' in request.GET:
            # If 'q' is present in the request, it performs a 
            # using the icontains filter.
            query = request.GET['q']
            if not query:
                messages.error(request, "You didn't enter any search criteria!")
                return redirect(reverse('products'))
            # case-insensitive search on product names and descriptions 
            queries = Q(name__icontains=query) | Q(description__icontains=query)
            products = products.filter(queries)

    # # Create a string representing the current sorting state
    current_sorting = f'{sort}_{direction}'    

    context = {
        'products': products,
        'search_term': query,
        'current_categories': categories,
        'current_sorting': current_sorting,
    }

    # Render the 'products/products.html' template with the created context
    return render(request, 'products/products.html', context)


def product_detail(request, product_id):
    """ A view to show individual product details """

    product = get_object_or_404(Product, pk=product_id)

    context = {
        'product': product,
    }

    return render(request, 'products/product_detail.html', context)