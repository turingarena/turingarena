def handle_evaluate(request):
    from turingarena_impl.evaluation.evaluate import evaluate
    from turingarena_impl.api.dynamodb_events import store_events

    store_events(request.evaluation_id, evaluate(request.evaluate_request))
