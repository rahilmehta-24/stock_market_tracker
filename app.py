from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import pandas as pd

app = Flask(__name__)

# Configure SQLite Database (Local)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the Portfolio model
class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    buyPrice = db.Column(db.Float, nullable=False)
    currentPrice = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Portfolio {self.symbol}>'

# Route for homepage (Dashboard)
@app.route('/')
def index():
    return render_template('index.html')

# Function to format numbers to Indian number format (e.g., 1,00,000 or 10,00,000)
def format_in_indian_number_format(number):
    if number is None:
        return "0"
    
    # Convert the number to a string
    num_str = str(number)
    # Reverse the number string for easier formatting
    num_str = num_str[::-1]
    
    # Add commas after every 2 digits, except the first group
    formatted = []
    for i in range(0, len(num_str), 3):
        formatted.append(num_str[i:i+3])
    
    # Reverse the groups back and join them with commas
    return ",".join(formatted)[::-1]


# Route for Portfolio Page with Summary and Top 5 Gainers/Losers
@app.route('/portfolio')
def portfolio():
    # Get the current page number from the request, default to 1 if not present
    page = request.args.get('page', 1, type=int)
    per_page = 20  # Show 20 records per page

    # Fetch all portfolio data for calculating gainers/losers
    all_stocks = Portfolio.query.all()
    portfolio = []
    total_invested = 0
    total_current_value = 0

    # Process all stocks to calculate total invested, total current value, and gain/loss
    for stock in all_stocks:
        gain_loss = (stock.currentPrice - stock.buyPrice) * stock.quantity
        portfolio.append({
            'id': stock.id,
            'symbol': stock.symbol,
            'quantity': stock.quantity,
            'buyPrice': stock.buyPrice,
            'currentPrice': stock.currentPrice,
            'gain_loss': gain_loss
        })

    total_invested = round(sum(stock['quantity'] * stock['buyPrice'] for stock in portfolio), 2)
    total_current_value = round(sum(stock['quantity'] * stock['currentPrice'] for stock in portfolio), 2)
    formatted_total_invested = format_in_indian_number_format(total_invested)
    formatted_total_current_value = format_in_indian_number_format(total_current_value)


    # Sort the portfolio based on gain/loss
    sorted_portfolio = sorted(portfolio, key=lambda x: x['gain_loss'], reverse=True)

    # Calculate Top 5 Gainers and Top 5 Losers (from the entire portfolio)
    top_gainers = sorted_portfolio[:5]
    top_losers = sorted(portfolio, key=lambda x: x['gain_loss'])[:5]

    # Fetch paginated portfolio data for the current page
    paginated_portfolio = Portfolio.query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template(
        'portfolio.html',
        total_invested=formatted_total_invested,
        total_current_value=formatted_total_current_value,
        top_gainers=top_gainers,
        top_losers=top_losers,
        pagination=paginated_portfolio
    )

# Route to Handle CSV Upload
@app.route('/upload-csv', methods=['POST'])
def upload_csv():
    file = request.files['csvFile']
    if not file:
        return jsonify({'message': 'No file uploaded'}), 400

    try:
        file_content = file.stream.read().decode("utf-8")
        df = pd.read_csv(StringIO(file_content))
        insert_data_into_db(df)
        return jsonify({'message': 'CSV uploaded and data inserted successfully'})
    except Exception as e:
        return jsonify({'message': f'Error processing file: {str(e)}'}), 500

# Function to Insert Data from CSV to Database
def insert_data_into_db(df):
    for index, row in df.iterrows():
        portfolio = Portfolio(
            symbol=row['symbol'],
            quantity=row['quantity'],
            buyPrice=row['buyPrice'],
            currentPrice=row['currentPrice']
        )
        db.session.add(portfolio)
    db.session.commit()

# Add Stock to Portfolio
@app.route('/add-stock', methods=['POST'])
def add_stock():
    symbol = request.form['symbol']
    quantity = float(request.form['quantity'])
    buy_price = float(request.form['buyPrice'])
    current_price = float(request.form['currentPrice'])

    portfolio = Portfolio(symbol=symbol, quantity=quantity, buyPrice=buy_price, currentPrice=current_price)
    db.session.add(portfolio)
    db.session.commit()

    return redirect('/portfolio')

# Update Stock Details
@app.route('/update-stock/<int:id>', methods=['POST'])
def update_stock(id):
    stock = Portfolio.query.get(id)
    if stock:
        stock.symbol = request.form['symbol']
        stock.quantity = float(request.form['quantity'])
        stock.buyPrice = float(request.form['buyPrice'])
        stock.currentPrice = float(request.form['currentPrice'])
        db.session.commit()
    return redirect('/portfolio')

# Delete a Stock
@app.route('/delete-stock/<int:id>', methods=['GET'])
def delete_stock(id):
    stock = Portfolio.query.get(id)
    if stock:
        db.session.delete(stock)
        db.session.commit()
    return redirect('/portfolio')

# Delete Entire Portfolio
@app.route('/delete-all', methods=['GET'])
def delete_all_stocks():
    try:
        Portfolio.query.delete()
        db.session.commit()
        return redirect('/')
    except Exception as e:
        return str(e), 500

# Run the App
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
