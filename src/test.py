from datetime import datetime

from collections import defaultdict


def calculate_cumulative_returns(portfolio_changes):
    # Create a defaultdict to store the cumulative returns for each stock
    cumulative_returns = defaultdict(float)

    # Iterate over each portfolio change
    for portfolio_change in portfolio_changes:
        # Get the stock name and number of shares
        stock_name = portfolio_change['stock']['name']
        shares = portfolio_change['stock']['shares']
        # Check if we are adding or removing a stock
        if portfolio_change['action'] == 'add':
            # Add the value of the stock to the cumulative returns
            cumulative_returns[stock_name] += shares * portfolio_change['stock']['price']
        elif portfolio_change['action'] == 'remove':
            # Subtract the value of the stock from the cumulative returns
            cumulative_returns[stock_name] -= shares * portfolio_change['stock']['price']

    # Create a list to store the cumulative returns over time
    cumulative_returns_over_time = []
    # Iterate over each stock in the cumulative returns dictionary
    for stock_name, value in cumulative_returns.items():
        # Add the cumulative return for this stock to the list
        cumulative_returns_over_time.append(
            {'name': stock_name, 'value': value, 'date': portfolio_change['stock']['date']})

    # Return the list of cumulative returns over time
    return cumulative_returns_over_time


def calculate_revenue(initial_capitals, capital_changes, portfolio_changes):
    # Create a dictionary to store the revenue for each person
    revenues = {}

    # Iterate over each person's initial capital
    for name, initial_capital in initial_capitals.items():
        # Set the starting revenue to the initial capital
        revenue = initial_capital

        # Create a list to store the current portfolio for this person
        portfolio = []

        # Create a dictionary to store the revenue history for this person
        revenue_history = {}

        # Add the initial capital as the first entry in the revenue history
        revenue_history[datetime.now().strftime('%Y-%m-%d')] = initial_capital

        # Iterate over each capital change for this person
        for capital_change in capital_changes:
            # Check if this capital change is for the current person
            if capital_change['name'] == name:
                # Check if we are adding or subtracting capital
                if capital_change['action'] == 'add':
                    # Add the capital change to the revenue
                    revenue += capital_change['amount']
                elif capital_change['action'] == 'subtract':
                    # Subtract the capital change from the revenue
                    revenue -= capital_change['amount']

                # Add the updated revenue to the revenue history
                revenue_history[capital_change['date'].strftime('%Y-%m-%d')] = revenue

        # Iterate over each portfolio change
        for portfolio_change in portfolio_changes:
            # Check if this portfolio change is for the current person
            if portfolio_change['name'] == name:
                # Check if we are adding or removing a stock
                if portfolio_change['action'] == 'add':
                    # Add the stock to the portfolio
                    portfolio.append(portfolio_change['stock'])
                elif portfolio_change['action'] == 'remove':
                    # Remove the stock from the portfolio
                    portfolio.remove(portfolio_change['stock'])

        # Iterate over each stock in the portfolio
        for stock in portfolio:
            # Get the current price of the stock
            stock_price = stock['price']
            # Get the number of shares of the stock
            shares = stock['shares']
            # Calculate the value of the stock in the portfolio
            stock_value = stock_price * shares
            # Add the value of the stock to the revenue
            revenue += stock_value

        # Store the revenue history for this person in the revenues dictionary
        revenues[name] = revenue_history

    # Return the revenues dictionary
    return revenues


if __name__ == "__main__":
    # Initial capital invested by each person
    initial_capitals = {
        'Antoine': 1500,
        'Arthur': 500
    }

    # List of capital changes for each person
    # Set the capital changes for each person
    capital_changes = [
        {'name': 'Antoine', 'action': 'add', 'amount': 100, 'date': datetime(2022, 2, 1)},
        {'name': 'Antoine', 'action': 'subtract', 'amount': 50, 'date': datetime(2022, 3, 1)},
        {'name': 'Arthur', 'action': 'add', 'amount': 50, 'date': datetime(2022, 2, 1)},
        {'name': 'Arthur', 'action': 'subtract', 'amount': 25, 'date': datetime(2022, 3, 1)}
    ]

    # List of portfolio changes for each person
    portfolio_changes = [
        {'name': 'Antoine', 'action': 'add',
         'stock': {'name': 'NVDA', 'shares': 2, 'price': 500, 'date': datetime(2021, 2, 23)}},
        {'name': 'Arthur', 'action': 'add',
         'stock': {'name': 'NVDA', 'shares': 2, 'price': 500, 'date': datetime(2021, 2, 23)}},
        {'name': 'Antoine', 'action': 'add',
         'stock': {'name': 'CRM', 'shares': 2, 'price': 400, 'date': datetime(2021, 2, 23)}},
        {'name': 'Arthur', 'action': 'add',
         'stock': {'name': 'CRM', 'shares': 2, 'price': 400, 'date': datetime(2021, 2, 23)}}
    ]

    # Calculate the revenue for each person
    revenues = calculate_revenue(initial_capitals, capital_changes, portfolio_changes)

    for name, revenue_history in revenues.items():
        # Print the name of the person
        print(name)
        # Iterate over each revenue in the history
        for date, revenue in revenue_history.items():
            # Print the date and revenue for this entry
            print(f'{date}: {revenue}')

    cumulative_returns = calculate_cumulative_returns(portfolio_changes)
    # Iterate over each cumulative return in the list
    for cumulative_return in cumulative_returns:
        # Print the stock name, cumulative return, and date
        print(
            f"Stock: {cumulative_return['name']} | Cumulative Return: {cumulative_return['value']} | Date: {cumulative_return['date']}")