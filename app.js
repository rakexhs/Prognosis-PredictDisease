const path = require('path');
const express = require('express');
const { spawn } = require('child_process');
const mysql = require('mysql');
const bodyParser = require('body-parser');
const app = express();
const PredictionTable = require('./predictionmodel'); 
const pool = mysql.createPool({
  host: 'localhost',
  user: 'root',
  password: '',
  database: 'trial'
});

//body-parser extracts the entire body portion of an 
//incoming request stream and exposes it on req.body.
app.use( express.static( "public" ) );
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));
app.get('/', (req, res) => {
  res.render('index');
});

app.get('/signup', (req, res) => {
  res.render('signup');
});

app.get('/login', (req, res) => {
  res.render('login');
});
app.get('/logout', (req, res) => {
  // Perform any necessary logout actions (e.g., clearing session, destroying tokens, etc.)
  
  // Then, render the "index" view after logout
  res.render('index');
});
app.get('/my-prediction', async (req, res) => {
  try {
    const { email, name } = req.query; // Get the name from the query parameters
    console.log('Requested email:', email);

    // Fetch predictions from the database where the email matches the requested email
    const predictions = await PredictionTable.findAll({
      attributes: ['symptoms', 'prediction'], // Retrieve only symptoms and prediction columns
      where: { email },
      group: ['symptoms', 'prediction'], // Group by symptoms and prediction columns
    });
    console.log('Retrieved predictions:', predictions);
    // Render the my_predictions.ejs template and pass the predictions and name data to it
    res.render('myprediction', { predictions, name }); // Pass the name to the template
  } catch (error) {
    console.error('Error:', error.message);
    res.status(500).send('An error occurred while fetching predictions.');
  }
});

app.post('/login', (req, res) => {
  try {
    const email = req.body.email;
    const password = req.body.password;

    if (!email || !password) {
      return res.status(400).render('login', {
        message: 'Please provide an email and password'
      });
    }

    pool.query('SELECT * FROM users WHERE email = ?', [email], (error, results) => {
      if (error) {
        console.log(error);
        return res.status(500).render('login', {
          message: 'Internal server error'
        });
      }

      let alertMessage = null; // Initialize the alertMessage variable to null
      let emaill=null;

      if (!results || password !== results[0].password) {
        alertMessage = 'Invalid credentials. Please try again.'; // Set the alertMessage to "INVALID"
        return res.status(401).render('login', {
          alertMessage: alertMessage // Pass the alertMessage to the template
        });
      }
      const fullName = results[0].name;
      const firstName = fullName.split(' ')[0]; // Extract the first name
      emaill=results[0].email;

      if (email === 'admin@gmail.com' && password === 'admin@123') {
        return res.status(200).render('Adminbase');
      } else {
        return res.status(200).render('base', {
          name: firstName,
          email: emaill
        });
      }
    });
  } catch (error) {
    console.log(error);
    res.status(500).render('login', {
      message: 'Internal server error'
    });
  }
});


app.post('/register', (req, res) => {
  const name = req.body.name;
  const dob = req.body.dob;
  const email = req.body.email;
  const phone = req.body.phone;
  const password = req.body.password;

  pool.query('INSERT INTO users (name, dob, email, phone, password) VALUES (?, ?, ?, ?, ?)', [name, dob, email, phone, password], (error, results, fields) => {
    if (error) {
      console.error(error);
      res.status(500).send('Error registering new user');
    } else {
      res.status(200).render('sussindex');
    }
  });
});
app.post('/savePrediction', (req, res) => {
  const { email, symptoms, prediction } = req.body; // Extract the email, symptoms, and prediction from the request body

  // Perform the database insertion
  pool.query('INSERT INTO predictiontable (email, symptoms, prediction) VALUES (?, ?, ?)', [email, symptoms, prediction], (error, results, fields) => {
    if (error) {
      console.error(error);
      res.status(500).send('Error Saving Prediction');
    } else {
      res.status(200).send('Prediction Saved Successfully');
    }
  });
});
app.listen(3000, () => {
  console.log('Server started on port 3000');
});
