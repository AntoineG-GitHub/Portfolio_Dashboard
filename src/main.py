# def main():
#     cashflows = pd.read_excel("Cashflows.xlsx", sheet_name="Cashflows")
#     ticker_portfolio = cashflows.groupby(['Ticker']).sum(['Quantity', 'Montant_total']).reset_index()[['Ticker', 'Quantity', 'Montant_total']]
#     ticker = ticker_portfolio.Ticker.tolist()
#     print(ticker)
#
#     actor_deposits = pd.read_excel("Cashflows.xlsx", sheet_name="Deposits")
#
#     price_update = yf.download(ticker[0], start='2019-01-01', end='2021-06-12', progress=False)
#     price_stock = px.line(price_update['Close'])


def main():
    from content import app
    import callbacks
    app.title = "Umbrella"
    app.run_server(debug=False, host='0.0.0.0')  # , host='0.0.0.0'


if __name__ == "__main__":
    main()
