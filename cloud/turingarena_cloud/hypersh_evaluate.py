def handle_evaluate(request):
    from turingarena_cloud.evaluate import cloud_evaluate
    from turingarena_cloud.dynamodb_events import store_events

    store_events(request.evaluation_id, cloud_evaluate(request.evaluate_request))
