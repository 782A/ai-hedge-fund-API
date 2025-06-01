# /app/my_django_project/api_integration/views.py
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt # For simplicity in example
import json

@csrf_exempt # Only for example, CSRF protection is important in production
def get_stock_analysis(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            tickers = data.get('tickers') # This should be a list of ticker strings
            selected_analysts = data.get('selectedAnalysts')
            model_name = data.get('modelName', 'gpt-4o') # Default if not provided

            if not tickers or not isinstance(tickers, list) or not selected_analysts:
                return JsonResponse({'error': 'Missing tickers (must be a list) or selectedAnalysts'}, status=400)

            api_url = 'http://localhost:6000/api/analysis' # Assuming the API runs here
            payload = {
                'tickers': tickers,
                'selectedAnalysts': selected_analysts,
                'modelName': model_name
            }

            # In a real scenario, the ai-hedge-fund-API needs to be running.
            # For now, we'll use a mock response, but the actual call is uncommented.
            # It will fail if the external API is not running.
            try:
                # response = requests.post(api_url, json=payload, timeout=30) # 30-second timeout
                # response.raise_for_status() # Raises an HTTPError for bad responses (4XX or 5XX)
                # api_data = response.json()

                # ---- MOCK RESPONSE FOR THIS CONCEPTUAL STAGE ----
                print(f"[DEBUG] Mocking API call to {api_url} with payload: {payload}")
                mock_api_data = {
                    "analyst_signals": {
                        f"mock_analyst_{analyst}": {
                            ticker: {"signal": "buy", "confidence": 0.9} for ticker in tickers
                        } for analyst in selected_analysts
                    },
                    "decisions": {
                        ticker: { "action": "buy", "quantity": 100, "reasoning": "Mocked strong buy signal."}
                        for ticker in tickers
                    }
                }
                api_data = mock_api_data
                # ---- END MOCK RESPONSE ----

            except requests.exceptions.RequestException as e:
                 # If the actual API call fails, return this error.
                 return JsonResponse({'error': f'API request failed: {str(e)}'}, status=503)

            return JsonResponse(api_data)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
