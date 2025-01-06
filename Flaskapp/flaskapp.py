from flask import Flask, request, render_template, redirect, url_for, session, flash
import boto3
from boto3.dynamodb.conditions import Key, Attr, And

app = Flask(__name__)
app.secret_key = '12345678'

# AWS Setup
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
login_table = dynamodb.Table('login')
music_table = dynamodb.Table('music')
subscription_table = dynamodb.Table('UserSubscriptions')

@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    response = login_table.get_item(Key={'email': email})
    if 'Item' in response and response['Item']['password'] == password:
        session['email'] = email  # Change session key to 'email'
        session['username'] = response['Item']['user_name']
        return redirect(url_for('main_page'))
    else:
        flash('Invalid email or password')
        return redirect(url_for('login_page'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        user_name = request.form['username']
        password = request.form['password']
        if email_exists(email):
            flash('The email already exists')
            return redirect(url_for('register'))
        else:
            login_table.put_item(Item={'email': email, 'user_name': user_name, 'password': password})
            flash('Registration successful. Please login.')
            return redirect(url_for('login_page'))
    return render_template('register.html')

def email_exists(email):
    response = login_table.get_item(Key={'email': email})
    return 'Item' in response

@app.route('/main', methods=['GET', 'POST'])
def main_page():
    if 'email' not in session:
        flash("Please login to view this page.")
        return redirect(url_for('login_page'))

    username = session.get('username')
    email = session.get('email')
    subscribed_music = get_user_subscriptions(email)

    if request.method == 'POST':
        title = request.form.get('title', '')
        artist = request.form.get('artist', '')
        year = request.form.get('year', '')
        results = query_music(title, artist, year)
        return render_template('main.html', username=username, subscribed_music=subscribed_music, results=results)
    
    return render_template('main.html', username=username, subscribed_music=subscribed_music, results=[])

def query_music(title, artist, year):
    expression_attribute_values = {}
    expression_attribute_names = {}
    filter_expressions = []

    if title:
        expression_attribute_values[':title'] = title
        expression_attribute_names['#title'] = 'title'
        filter_expressions.append('contains(#title, :title)')

    if artist:
        expression_attribute_values[':artist'] = artist
        expression_attribute_names['#artist'] = 'artist'
        filter_expressions.append('contains(#artist, :artist)')

    if year:
        expression_attribute_values[':year'] = year
        expression_attribute_names['#year'] = 'year'
        filter_expressions.append('#year = :year')

    if filter_expressions:
        filter_expression = ' AND '.join(filter_expressions)
        response = music_table.scan(
            FilterExpression=filter_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values
        )
        items = response.get('Items', [])
        
        # Construct image_url for each item
        for item in items:
            artist_name = item.get('artist', 'Unknown Artist')
            # Format the artist name to match the naming convention of the images
            formatted_artist_name = '_'.join(word.capitalize() for word in artist_name.split())
            image_filename = f"{formatted_artist_name}_{formatted_artist_name}.jpg"
            item['image_url'] = f"https://mohamed-manzoor.s3.amazonaws.com/artist_images/{image_filename}"

        return items
    return []

@app.route('/subscribe', methods=['POST'])
def subscribe_music():
    if 'email' not in session:
        flash('You must be logged in to subscribe.')
        return redirect(url_for('login_page'))

    title = request.form['title']
    try:
        music_response = music_table.get_item(Key={'title': title})
        if 'Item' in music_response:
            music = music_response['Item']
            # Split the artist name, capitalize the first letter of each part, and join with underscores
            artist_name_parts = music.get('artist', 'Unknown Artist').split()
            formatted_artist_name = '_'.join(part.capitalize() for part in artist_name_parts)
            image_filename = f"{formatted_artist_name}_{formatted_artist_name}.jpg"
            image_url = f"https://mohamed-manzoor.s3.amazonaws.com/artist_images/{image_filename}"

            subscription_item = {
                'email': session['email'],
                'title': music['title'],
                'artist': music.get('artist', 'Unknown Artist'),
                'year': music.get('year', 'Unknown Year'),
                'image_url': image_url  # Dynamically constructed image URL
            }
            subscription_table.put_item(Item=subscription_item)
            flash('Subscribed successfully!')
        else:
            flash('Music not found.')
    except Exception as e:
        flash(f'An error occurred: {str(e)}')

    return redirect(url_for('main_page'))

@app.route('/remove', methods=['POST'])
def remove_music():
    title = request.form['title']
    try:
        subscription_table.delete_item(
            Key={
                'email': session['email'],
                'title': title
            }
        )
        flash('Subscription removed!')
    except Exception as e:
        flash(f'An error occurred: {str(e)}')

    return redirect(url_for('main_page'))

def get_user_subscriptions(email):
    try:
        response = subscription_table.query(
            KeyConditionExpression=Key('email').eq(email)
        )
        return response.get('Items', [])
    except Exception as e:
        flash(f'An error occurred: {str(e)}')
        return []

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('login_page'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
