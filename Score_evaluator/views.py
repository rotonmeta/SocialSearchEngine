from django.shortcuts import render, redirect
from .models import CategoryScore
import pysolr
import threading
from app.views import initialize_context

solr = pysolr.Solr('https://solr.socialsearch.blog/solr/demo3/')


def similarity(request):
    if request.user.is_anonymous:
        return render(request, 'Score_evaluator/similarity.html', {'profpic': 0})

    if not request.session.get('search_done'):
        initialize_context(request)

    if not request.session.get('similarity_done'):
        context = request.session['context']
        user_id = context['user_id']

        # Getting top 5 liked categories for the user.
        top_categories = CategoryScore.objects.filter(user__uid=user_id)\
            .values('category__name')\
            .order_by('-likes')[:5]
        category_list = [x['category__name'] for x in top_categories]
        context.update({'category_list': category_list})

        # Getting 10 most similar users to the current user.
        user_list = []
        for score in context['score_list'][:10]:
            user_id_ = score['users']
            user_id_.remove(user_id)
            details = solr.search(q='doc_type:user AND user_id:' + user_id_[0],
                                  fl='user_name, user_profile_picture',
                                  rows=1, wt='python').docs[0]
            user_list.append(details)
        context.update({'user_list': user_list})

        # Update session variable 'context'
        request.session['context'] = context

        # Save session variable to know that this view has been already executed
        request.session['similarity_done'] = True

    context = request.session['context']
    return render(request, 'Score_evaluator/similarity.html', context)

