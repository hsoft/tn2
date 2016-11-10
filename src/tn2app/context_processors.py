def tn2_processor(request):
    return {
        'can_write_article': request.user.has_perm('tn2app.add_article'),
    }

