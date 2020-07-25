
# Code By - Mr.Ritesh Desai
# Please contact me on desairitesh1994@gmail.com to get access to private repository with complete code.

from flask import Flask, render_template, url_for, request, session, redirect, jsonify
from flask_pymongo import PyMongo
import bcrypt

#Uncomment when data is to be written on RFID card.
#import RPi.GPIO as GPIO
#from mfrc522 import SimpleMFRC522

app = Flask(__name__)

app.config['MONGO_DBNAME'] = ''
app.config['MONGO_URI'] = '' #mlab_url

mongo = PyMongo(app)

@app.route('/')
def index():

    #Will display home page if session is active.Entry point for Application.
    if 'username' in session:
        return render_template('homepage.html', message = ' Welcome back !!! ' + session['username'] )

    return render_template('index.html', message = ' All fields are mandatory !!! ')

@app.route('/homepage')
def homepage():

    #Will display home page.
    if 'username' in session:
        return render_template('homepage.html', message = ' Welcome !!! ' + session['username'] )

    return render_template('index.html', message = ' All fields are mandatory !!! ')

@app.route('/aboutus')
def aboutus():

    #Will display about us page.
    return render_template('aboutus.html')

@app.route('/contactus')
def contactus():

    #Will display contact us page.
    return render_template('contactus.html')

@app.route('/logout')
def logout():

    #Will end session and logout user.
    if 'username' in session:
        session.pop('username', None)
        return render_template('index.html', message = ' Good Bye !!! Have a Nice Day ')

    return render_template('index.html', message = ' Log In Required !!! ')

@app.route('/login', methods=['POST'])
def login():

    #Will verify user credentials.
    users = mongo.db.users
    login_user = users.find_one({'name' : request.form['username']})

    if login_user:
        if bcrypt.checkpw(request.form['pass'].encode('utf-8'), login_user['password']):
            session['username'] = request.form['username']
            return render_template('homepage.html', message = ' Welcome !!! ' + session['username'] )

        return render_template('index.html', message = ' Invalid username/password combination !!! ')

    return render_template('index.html', message = ' No registered user with this username !!! ')

@app.route('/register', methods=['POST', 'GET'])
def register():

    #Will add new user in database. 
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name' : request.form['username']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            users.insert({'name' : request.form['username'], 'password' : hashpass})
            session['username'] = request.form['username']
            return render_template('index.html', message = ' User registered successfully !!! ')
        
        return render_template('index.html', message = ' Username already exists !!! Please try with other name. ')

    if request.method == 'GET':

        #Will display UI to add user. 
        return render_template('register.html', message = ' All fields are mandatory !!! ')

@app.route('/addorupdateproduct', methods=['POST', 'GET'])
def addorupdateproduct():

    if request.method == 'POST':

        #Will add or update an existing product.
        products = mongo.db.products
        existing_product = products.find_one({'productid' : request.form['productid']})

        if existing_product is None:
            #New
            products.insert({   'productid'         : request.form['productid'],
                                'productname'       : request.form['productname'],
                                'productquantity'   : request.form['productquantity'],
                                'priceperunitquantity'      : request.form['priceperunitquantity'],
                                'productdiscount'   : request.form['productdiscount'],
                                'productaddedby'    : session['username']
                            })
            return render_template('product.html', message = ' Product added successfully !!! ', username = session['username'])
        
        #Update exisitng
        products.update_one({'productid': request.form['productid']},
                            {'$set': {
                                'productname'       : request.form['productname'],
                                'productquantity'   : request.form['productquantity'],
                                'priceperunitquantity'      : request.form['priceperunitquantity'],
                                'productdiscount'   : request.form['productdiscount'],
                                'productaddedby'    : session['username']
                                }
                            })

        return render_template('product.html', message = ' Product updated successfully !!! ', username = session['username'])
    
    if request.method == 'GET':

        #Will be called when user wishes to add or update an existing product. 
        return render_template('product.html', username = session['username'] )

@app.route('/deleteproduct', methods=['POST', 'GET'])
def deleteproduct():

    if request.method == 'POST':

        #Delete a product from database on basis of entered Product Id.
        products = mongo.db.products
        existing_product = products.find_one({'productid' : request.form['productid']})

        if existing_product is None:
            return render_template('deleteproduct.html', message = ' No matching Product found !!! ')
        
        products.delete_one({'productid': request.form['productid']})
        return render_template('deleteproduct.html', message = ' Product deleted successfully !!! ')

    if request.method == 'GET':

        #Will be called when user wish to delete a product from database.
        return render_template('deleteproduct.html', message = ' Enter Product Id !!! ')

@app.route('/order', methods=['GET'])
def order():

    #Will be called when user wishes to add a new order.
    if 'username' in session:
        products = mongo.db.products

        output = []
        for product in products.find():
            output.append({ 'productid' : product['productid'],
                            'productname' : product['productname'],
                            'productquantity' : product['productquantity'],
                            'priceperunitquantity' : product['priceperunitquantity'],
                            'productdiscount' : product['productdiscount']
                            })
    
        return render_template('order.html', container = output)
        #Please ensure that card is placed on the Read/Write Module after order page is displayed and prior to pressing OK.
    
    return render_template('index.html', message = ' Log In Required !!! ')

@app.route('/addorder', methods=['POST'])
def addorder():

    #Business Logic for Adding Order.
    #Please ensure that card is placed on the Read/Write Module before this is triggred.
    if 'username' in session:
        
        ordercontent = str("")        

        if request.form['productid1'] and request.form['productquantity1']:
            product1 = request.form['productid1'] + "$" +request.form['productquantity1']
            ordercontent = ordercontent + product1
        
        if request.form['productid2'] and request.form['productquantity2']:
            product2 = request.form['productid2'] + "$" +request.form['productquantity2']
            ordercontent = ordercontent + "#" + product2
        
        if request.form['productid3'] and request.form['productquantity3']:
            product3 = request.form['productid3'] + "$" +request.form['productquantity3']
            ordercontent = ordercontent + "#" + product3
        
        if request.form['productid4'] and request.form['productquantity4']:
            product4 = request.form['productid4'] + "$" +request.form['productquantity4']
            ordercontent = ordercontent + "#" + product4
        
        if request.form['productid5'] and request.form['productquantity5']:
            product5 = request.form['productid5'] + "$" +request.form['productquantity5']
            ordercontent = ordercontent + "#" + product5

    
        if ordercontent is str(""):
            return render_template('homepage.html', message = ' Failed to add Order : No order content !!! ', username = session['username']) 

        #For now : Due to some limitation in implementing self incrementing order id.Here user will be manually entering 
        #          order id which will be fetched from Text Box.It will be placed in a 'orderid' variable.
        orderid = request.form['orderid']

        if orderid is str(""):
            return render_template('homepage.html', message = ' Failed to add Order : Order Id is empty !!! ', username = session['username'])      
            
        orders = mongo.db.orders
        orders.insert({     'orderid'         : orderid,
                            'ordercontent'    : ordercontent,
                            'orderaddedby'    : session['username']
                    })  

        #PLACE CARD ON WRITER
        #Code to Write order Id (Write) to Card.

        #writer = SimpleMFRC522()

        #try:
	        #writer.write(orderid)

        #finally:
	        #GPIO.cleanup()

        return render_template('homepage.html', message = ' Order added successfully !!! ', username = session['username'])      
    
    return render_template('index.html', message = ' Log In Required !!! ')

@app.route('/orderidforbill', methods=['GET'])
def orderidforbill():

    #Triggered when order is to billed.
    if 'username' in session:
        #Will be called when user wish to bill a order from database.
        return render_template('orderidforbill.html', message = ' Enter Order Id !!! ')
    
    return render_template('index.html', message = ' Log In Required !!! ')
        

@app.route('/bill', methods=['POST'])
def bill():

    #Triggered when order is to billed.
    if 'username' in session:
        orders = mongo.db.orders
        products = mongo.db.products

        #Result that will be sent to UI
        output = []
        
        #PLACE CARD ON READER
        #Code to fetch order Id (READ) from Card will be done here.It will be placed in a 'orderid' variable.

        # reader = SimpleMFRC522()

        #try:
	        #id, text = reader.read()
            #The text variable here will contain the orderid.

        #finally:
	        #GPIO.cleanup()

        #For now : Order Id will be fetched from Text Box.It will be placed in a 'orderid' variable.
        orderid = request.form['orderid'] 

        #Fetch order from Orders table with particular Id
        order = orders.find_one({'orderid' : orderid})
        ordercost = 0

        if order:
            #Fetch order content in variable
            content = order['ordercontent']
            container = content.split("#")
            for item in container:
                sub_item = item.split("$")
                productid       = sub_item[0]
                productquantity = float(sub_item[1])
                product = products.find_one({'productid' : productid})
                if product is not None:
                    productprice = float(product['priceperunitquantity']) * productquantity
                    if not float(product['productdiscount']) is 0:
                        multiplier = 100 - float(product['productdiscount'])
                        factor = float(multiplier/100)
                        productprice = float(productprice * factor) 
                    ordercost = ordercost + productprice
                    output.append({ 'productid'         : productid,
                                    'productname'       : product['productname'],
                                    'productquantity'   : productquantity,
                                    'priceperunitquantity' : product['priceperunitquantity'],
                                    'productdiscount'      : product['productdiscount'],
                                    'productprice'         : productprice
                                })
            return render_template('bill.html', container = output, billamount= ordercost)
        
        return render_template('homepage.html', message = ' Order Id is Invalid !!! ', username = session['username'])

    return render_template('index.html', message = ' Log In Required !!! ')

@app.route('/updateorder', methods=['POST', 'GET'])
def updateorder():

    if request.method == 'POST':

        #Business Logic for updating existing Order.
        #Please ensure that card is placed on the Read/Write Module before this is triggred.        
        if 'username' in session:
            
            orders = mongo.db.orders

            #PLACE CARD ON READER
            #Code to fetch order Id (READ) from Card will be done here.It will be placed in a 'orderid' variable.

            #reader = SimpleMFRC522()

            #try:
	            #id, text = reader.read()
                #The text variable here will contain the orderid.

            #finally:
	            #GPIO.cleanup()

            #For now : Order Id will be fetched from Text Box.It will be placed in a 'orderid' variable.
            orderid = request.form['orderid']       
            
            #Fetch order from Orders table with particular Id
            order = orders.find_one({'orderid' : orderid})
            ordercontent = str("")

            if order is None:
                return render_template('homepage.html', message = ' Order Id is Invalid !!! ', username = session['username'])
            ordercontent = order['ordercontent']

            if request.form['productid1'] and request.form['productquantity1']:
                product1 = request.form['productid1'] + "$" +request.form['productquantity1']
                ordercontent = ordercontent + "#" + product1
        
            if request.form['productid2'] and request.form['productquantity2']:
                product2 = request.form['productid2'] + "$" +request.form['productquantity2']
                ordercontent = ordercontent + "#" + product2
        
            if request.form['productid3'] and request.form['productquantity3']:
                product3 = request.form['productid3'] + "$" +request.form['productquantity3']
                ordercontent = ordercontent + "#" + product3
        
            if request.form['productid4'] and request.form['productquantity4']:
                product4 = request.form['productid4'] + "$" +request.form['productquantity4']
                ordercontent = ordercontent + "#" + product4
        
            if request.form['productid5'] and request.form['productquantity5']:
                product5 = request.form['productid5'] + "$" +request.form['productquantity5']
                ordercontent = ordercontent + "#" + product5

            if ordercontent is str(""):
                return render_template('homepage.html', message = ' Failed to update Order : No order content !!! ', username = session['username']) 

            orders.update_one({'orderid': orderid},
                                {'$set': {
                                    'ordercontent'      : ordercontent,
                                    'orderaddedby'      : session['username']
                                }
                            })

            return render_template('homepage.html', message = ' Order updated successfully !!! ', username = session['username'])
    
        return render_template('index.html', message = ' Log In Required !!! ')

    if request.method == 'GET':

        #Code to fetch order from order id and show it in tabular form.When user updates order and press OK then the above post method will be called.

        #For Now : Previously entered products part of order will not be displayed in table.
        if 'username' in session:
            products = mongo.db.products

            output = []
        
            for product in products.find():
                output.append({ 'productid' : product['productid'],
                                'productname' : product['productname'],
                                'productquantity' : product['productquantity'],
                                'priceperunitquantity' : product['priceperunitquantity'],
                                'productdiscount' : product['productdiscount']
                            })
    
            return render_template('updateorder.html', container = output)
                #Please ensure that card is placed on the Read/Write Module after order page is displayed and prior to pressing OK.
    
        return render_template('index.html', message = ' Log In Required !!! ')

@app.route('/finish', methods=['POST'])
def finish():

    if request.method == 'POST':
        if 'username' in session:

            #PLACE CARD ON READER
            #<ToDo> : Code will clear data from card.

            #####
            ####
            ###
            ##
            #

            return render_template('homepage.html', message = ' Order Executed !!! ', username = session['username'])        

        return render_template('index.html', message = ' Log In Required !!! ')

@app.route('/write', methods=['POST', 'GET'])
def write():

    if request.method == 'POST':
        if 'username' in session:

            #Order Id will be fetched from Text Box.It will be placed in a 'orderid' variable.
            #orderid = request.form['orderid'];  
            #writer = SimpleMFRC522()

            #try:
	            #writer.write(orderid)

            #finally:
	            #GPIO.cleanup()
            return render_template('homepage.html', message = ' Success : Data write !!! ')

        return render_template('index.html', message = ' Log In Required !!! ')
     
    if request.method == 'GET':
        if 'username' in session:
            #<ToDo> : Add Code to display template to enter order id.
            return render_template('index.html', message = ' Awwwww!!! ')

        return render_template('index.html', message = ' Log In Required !!! ')

@app.route('/read', methods=['GET'])
def read():

    if request.method == 'GET':
        if 'username' in session:
            
            #reader = SimpleMFRC522()

            #try:
	            #id, text = reader.read()
                #The text variable here will contain the orderid.

            #finally:
	            #GPIO.cleanup()
            #<ToDo> : Will print contents of Card as message.
            return render_template('homepage.html', message = ' Data in Card : ')

        return render_template('index.html', message = ' Log In Required !!! ')

@app.route('/erase', methods=['GET'])
def erase():
     
    if request.method == 'GET':
        if 'username' in session:
            #PLACE CARD ON READER
            #<ToDo> : Code will clear data from card.

            #####
            ####
            ###
            ##
            #
            return render_template('homepage.html', message = ' Success : Data Erased from Card !!! ')

        return render_template('index.html', message = ' Log In Required !!! ') 

@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html'), 404

if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(debug=True)
