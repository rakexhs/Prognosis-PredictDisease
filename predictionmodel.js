const Sequelize = require('sequelize');
const sequelize = new Sequelize('trial', 'root', '', {
  host: 'localhost',
  dialect: 'mysql',
});

const PredictionTable = sequelize.define('predictiontable', {
  email: {
    type: Sequelize.STRING,
    primaryKey: true, // Specify email as part of the primary key
    allowNull: false,
  },
  symptoms: {
    type: Sequelize.STRING,
    primaryKey: true, // Specify symptoms as part of the primary key
    allowNull: false,
  },
  prediction: {
    type: Sequelize.STRING,
    primaryKey: true, // Specify prediction as part of the primary key
    allowNull: false,
  },
}, {
  tableName: 'predictiontable', // Specify the correct table name here
  timestamps: false, // If you don't want Sequelize to manage createdAt and updatedAt fields
});

module.exports = PredictionTable;
