# analysis/views.py
import json
import requests # To make requests to our own Django app's API endpoint
from django.shortcuts import render, redirect
from django.urls import reverse # To call our own api_integration view
from django.contrib.auth.decorators import login_required
from django.conf import settings # Potentially for API URL
from .forms import StockAnalysisForm
from django.contrib import messages
from django.http import HttpResponse # For placeholder if needed

@login_required
def request_analysis_view(request):
    form = StockAnalysisForm()
    analysis_results = None
    raw_json_results = None # For displaying the raw JSON in template

    if request.method == 'POST':
        form = StockAnalysisForm(request.POST)
        if form.is_valid():
            tickers_input = form.cleaned_data['tickers']
            # Split tickers string into a list, strip whitespace
            tickers_list = [ticker.strip().upper() for ticker in tickers_input.split(',')]

            selected_analysts = form.cleaned_data['selected_analysts']
            model_name = form.cleaned_data['model_name']

            # Prepare payload for our internal API endpoint (/api/get-analysis/)
            # The internal API endpoint (api_integration.views.get_stock_analysis)
            # expects 'tickers' to be a list of strings.
            payload = {
                'tickers': tickers_list,
                'selectedAnalysts': selected_analysts,
                'modelName': model_name
            }

            try:
                internal_api_url = request.build_absolute_uri(reverse('get_stock_analysis'))
                print(f"[DEBUG] Calling internal API: {internal_api_url} with payload: {payload}")

                # Pass along the user's session cookies for authentication if needed by the internal API
                # response = requests.post(internal_api_url, json=payload, cookies=request.COOKIES, timeout=60)
                # response.raise_for_status()
                # analysis_results = response.json()
                # raw_json_results = json.dumps(analysis_results, indent=2)
                # messages.success(request, "Analysis retrieved successfully!")

                # ---- MOCK RESPONSE FOR THIS CONCEPTUAL STAGE ----
                print(f"[DEBUG] Mocking internal API call to {internal_api_url} with payload: {payload}")
                mock_data = {
                    "analyst_signals": {
                        analyst: {
                            ticker: {"signal": "buy", "confidence": 0.9, "reasoning": f"Mocked strong buy signal for {ticker} from {analyst}"}
                            for ticker in tickers_list
                        } for analyst in selected_analysts
                    },
                    "decisions": {
                        ticker: { "action": "buy", "quantity": 100, "reasoning": f"Mocked overall decision for {ticker} based on selected analysts."}
                        for ticker in tickers_list
                    }
                }
                analysis_results = mock_data
                raw_json_results = json.dumps(analysis_results, indent=2) # For display
                messages.success(request, "Mock analysis retrieved successfully!")
                # ---- END MOCK RESPONSE ----

            except requests.exceptions.RequestException as e:
                messages.error(request, f"Error fetching analysis: {e}")
                print(f"[ERROR] Error calling internal API: {e}")
                analysis_results = None
                raw_json_results = json.dumps({'error': str(e)}, indent=2)
            except Exception as e:
                messages.error(request, f"An unexpected error occurred: {e}")
                print(f"[ERROR] Unexpected error: {e}")
                analysis_results = None
                raw_json_results = json.dumps({'error': str(e)}, indent=2)
        else:
            messages.error(request, "Please correct the errors in the form.")

    return render(request, 'analysis/request_analysis.html', {
        'form': form,
        'analysis_results': analysis_results,
        'raw_json_results': raw_json_results,
    })
