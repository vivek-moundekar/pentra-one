from django.shortcuts import render, get_object_or_404, redirect
from .models import GovernmentScheme


def scheme_list(request):
    schemes = GovernmentScheme.objects.filter(is_active=True)

    language = request.session.get('scheme_language', 'en')

    return render(
        request,
        'government_schemes/scheme_list.html',
        {
            'schemes': schemes,
            'language': language
        }
    )


def scheme_detail(request, slug):
    scheme = get_object_or_404(
        GovernmentScheme,
        slug=slug,
        is_active=True
    )

    language = request.session.get('scheme_language', 'en')

    return render(
        request,
        'government_schemes/scheme_detail.html',
        {
            'scheme': scheme,
            'language': language
        }
    )


def scheme_category(request, category):
    schemes = GovernmentScheme.objects.filter(
        category=category,
        is_active=True
    )

    language = request.session.get('scheme_language', 'en')

    return render(
        request,
        'government_schemes/scheme_list.html',
        {
            'schemes': schemes,
            'category': category,
            'language': language
        }
    )


def scheme_search(request):
    query = request.GET.get('q', '')

    schemes = GovernmentScheme.objects.filter(
        is_active=True
    )

    if query:
        schemes = schemes.filter(
            name__icontains=query
        )

    language = request.session.get('scheme_language', 'en')

    return render(
        request,
        'government_schemes/scheme_list.html',
        {
            'schemes': schemes,
            'query': query,
            'language': language
        }
    )


def set_scheme_language(request, language):
    allowed_languages = ['en', 'mr', 'hi']

    if language in allowed_languages:
        request.session['scheme_language'] = language

    return redirect(
        request.META.get(
            'HTTP_REFERER',
            '/government-schemes/'
        )
    )
# Create your views here.
