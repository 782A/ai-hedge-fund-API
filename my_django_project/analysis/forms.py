# analysis/forms.py
from django import forms

# Example: Get analyst choices from a predefined list or settings
# In a real app, this might come from a config file or database
ANALYST_CHOICES = [
    ('ben_graham', 'Ben Graham'),
    ('warren_buffett', 'Warren Buffett'), # Assuming these are valid for the API
    ('ray_dalio', 'Ray Dalio'),
    ('peter_lynch', 'Peter Lynch'),
    ('george_soros', 'George Soros'),
]

MODEL_CHOICES = [ # Assuming these are valid LLM model names for the API
    ('gpt-4o', 'GPT-4o (OpenAI)'),
    ('gpt-4-turbo', 'GPT-4 Turbo (OpenAI)'),
    ('claude-3-opus-20240229', 'Claude 3 Opus (Anthropic)'),
    ('claude-3-sonnet-20240229', 'Claude 3 Sonnet (Anthropic)'),
    ('llama3-70b-8192', 'LLaMA3 70B (Meta via Groq)'),
]

class StockAnalysisForm(forms.Form):
    tickers = forms.CharField(
        label='Stock Ticker(s)',
        help_text='Enter stock tickers separated by commas (e.g., TSLA, AAPL, MSFT)',
        widget=forms.TextInput(attrs={'placeholder': 'e.g., TSLA, AAPL, NVDA', 'class': 'form-control'})
    )
    selected_analysts = forms.MultipleChoiceField(
        label='Select AI Analyst(s)',
        choices=ANALYST_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        help_text='Choose one or more analysts for the evaluation.'
    )
    model_name = forms.ChoiceField(
        label='Select Large Language Model',
        choices=MODEL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text='Choose the LLM to power the analysis.'
    )
