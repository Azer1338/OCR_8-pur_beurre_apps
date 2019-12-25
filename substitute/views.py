from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect

from .console_display import console_display
from .models import Aliment, UserLinkToAlimentsTable


def search_view(request):
    """
    Display a list of similar aliments based on user's query.
    :param request: User's request
    :return:
    """

    # Collect the User's request
    query = request.GET.get('userSearch')
    # Display
    console_display("User's request: " + str(query))

    # Ensure that the query is filled
    if query:
        # Gather a list from database
        aliment_name = Aliment.objects.filter(name__icontains=query)
        # Check if we find some elements
        if not aliment_name.exists():
            # No result found message
            message = "Misère de misère, nous n'avons trouvé aucun résultat !"
            aliment_list = []
        else:
            # Look for similar aliment
            message = "Vous pouvez remplacer cet aliment par:"
            # Collect a list of aliment with the same categories
            aliment_list = Aliment.objects.\
                filter(category__icontains=aliment_name[0].category).\
                order_by('nutrition_score')

    else:
        # No query send
        message = "Vous n'avez pas spécifié votre recherche. Voici notre liste."
        aliment_list = Aliment.objects.all().order_by('name')

    # Slice page
    paginator = Paginator(aliment_list, 6)
    # Get the current page
    page = request.GET.get('page')

    # Return only this page substitute and not others
    try:
        aliments = paginator.page(page)
        print("Page OK")
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        aliments = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        aliments = paginator.page(paginator.num_pages)

    # Build the context
    context = {
        'substitutes': aliments,

        'user_request': query,
        'message': message,

        'paginate': True,
    }

    return render(request, 'substitute/search.html', context)


def detail_view(request, aliment_id):
    """
    Display the details of an aliment.
    :param request:
    :param aliment_id:
    :return:
    """

    # Get the aliment from his id
    aliment = Aliment.objects.get(pk=aliment_id)

    messages.add_message(request, messages.INFO, 'Hello world.')

    context = {
        'aliment': aliment,
        # 'messages': messages,
    }

    return render(request, 'substitute/details.html', context)


def favorites_view(request):
    """
    Display only the favorites substitutes.
    :param request:
    :return:
    """
    favorite_list = 0

    # Ensure that an user is authentified
    if request.user.is_authenticated:
        # Gather a list from database
        favorites_id_list = UserLinkToAlimentsTable.objects.filter(user_id=request.user)
        # Check if we find some elements
        if not favorites_id_list.exists():
            # List is empty
            message = "Misère de misère, vous n'avez encore pas enregistrer de favoris !"
            # Empty list
            favorite_list = []
        else:
            # Some elements are in the list
            message = "Voici vos favoris"
            # Collect the aliments from the list
            favorite_list = []
            for elt in favorites_id_list:
                adrien = Aliment.objects.filter(id=elt.aliment_id).distinct()
                favorite_list.extend(adrien)

    else:
        # User is not identified
        message = "Vous devez etre identifié pour voir vos favoris"

    # Slice page
    paginator = Paginator(favorite_list, 6)
    # Get the current page
    page = request.GET.get('page')

    # Return only this page substitute and not others
    try:
        favorite = paginator.page(page)
        print("Page OK")
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        favorite = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        favorite = paginator.page(paginator.num_pages)

    # Build the context
    context = {
        'substitutes': favorite,
        'message': message,
        'paginate': True,
    }

    return render(request, 'substitute/favorite.html', context)


def save_view(request, aliment_id):
    """
    Save the aliment selected as favorite in the database
    :param request:
    :param aliment_id:
    :return:
    """

    # Add the favorite aliment in the table
    UserLinkToAlimentsTable.objects.create(user_id=request.user, aliment_id=aliment_id)

    messages.success(request, 'Aliment ajouté!')

    return redirect(request.META['HTTP_REFERER'])


def delete_view(request, aliment_id):
    """
    Remove the aliment selected as favorite in the database
    :param request:
    :param aliment_id:
    :return:
    """

    # Add the favorite aliment in the table
    UserLinkToAlimentsTable.objects.filter(user_id=request.user, aliment_id=aliment_id).delete()

    messages.success(request, 'Aliment retiré!')

    return redirect(request.META['HTTP_REFERER'])
