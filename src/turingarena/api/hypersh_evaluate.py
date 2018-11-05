def handle_evaluate(request):
    from turingarena.evaluation.evaluate import cloud_evaluate
    from turingarena.api.dynamodb_events import store_events

    store_events(request.evaluation_id, cloud_evaluate(request.evaluate_request))
