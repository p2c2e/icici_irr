# icici_irr
Calculating IRR (Internal Rate of Return) for investments made through ICICIDirect

ICICIDirect portfolio tools show a simple percentage gain or loss. This is superficial and very rarely means anything.

For e.g.:
If I invested I had invested 100$ and today's value is 110$, the reports would show 10% increase in value.
Does it matter _when_ I invested the 100$? Of course, it should. if I had invested the amount exactly an year back, then the return would be 10%. What if I had invested the money 2 years back?

The formula for IRR is:
https://i.investopedia.com/u53826/npv_formula.png

Calculating 'r' in the formula is through trial-and-error. In Excel, we could use the IRR() function with an initial guess.

Things can get hairy if you have lots of investments, many of them with systematic investment plans (SIPs) - usually on a monthly basis.

I wrote a small script in Python using NumPy and Pandas to address this requirement. The code uses the *fsolve* function to find the rate of return.

Suggested way to use:
- Download the yearly orderbook xls files to a subfolder named  : 'OrderBooks'
- Download the dividend history (maybe in multiple files over multiple periods) to a subfolder named : 'Dividends'
- Download the latest portfolio/positions to the current folder (where the Orders.py is located)
- Run the code as : 
```
python Orders.py
```
