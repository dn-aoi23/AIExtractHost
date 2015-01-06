#!/usr/bin/env python
import os
from flask import Flask, abort, request, jsonify, g, url_for
from flask.ext.sqlalchemy import SQLAlchemy #needed for db
#from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from flask.ext.restful import Api, Resource, reqparse, fields, marshal

# initialization
app = Flask(__name__, static_url_path = "")
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///records.db' #db file
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True #commit session when app context is torn down

# extensions
db = SQLAlchemy(app)
api = Api(app)
HATEOAS = True
CSRF_ENABLED = True

#--------------------------
# Start of DATABASE CLASS 
#--------------------------

class Drugstores(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	storename = db.Column(db.String(80))
	address = db.Column(db.String(1000), unique=True)
	province = db.Column(db.String(50))
	manager = db.Column(db.String(100))
		
class Drugs(db.Model): #table for available drugs
    id = db.Column(db.Integer, primary_key = True) #column for available drugs id
    generic = db.Column(db.String(50))
    brand = db.Column(db.String(50), unique=True)
    strength = db.Column(db.String(100))
    form = db.Column(db.String(20))

#------------------------
# End of DATABASE CLASS
#-----------------------

#-------------
# Start of API 
#-------------

class DrugstoreListAPI(Resource):

	def get(self, page=1):
		cols = ['id','storename','address','province','manager']
		stores = Drugstores.query.paginate(page, 50, True)
		result = [{col: getattr(d, col) for col in cols} for d in stores.items]
		return jsonify(stores=result)

		# if stores.has_prev:
		# 	page = stores.prev_num
		# if stores.has_next:
		# 	page = stores.next_num

class DrugstorePostingAPI(Resource):

	def post(self, page=1):
		storename = request.form['storename']
		address = request.form['address']
		province = request.form['province']
		manager = request.form['manager']

		store = Drugstores(storename=storename, address=address, province=province, manager=manager)
		db.session.add(store)
		db.session.commit()
		return {'storename':store.storename,'address':store.address,'province':store.province,'manager':store.manager,'id':store.id}, 201

	def post(self):
		storename = request.form['storename'].title()
		cols = ['id','storename','address','province','manager']
		store = Drugstores.query.filter_by(storename=storename).all()
		result = [{col: getattr(d, col) for col in cols} for d in store]
		return jsonify(store=result)

	# def post(self):
	# 	province = request.form['province'].title()
	# 	cols = ['id','storename','address','province','manager']
	# 	store = Drugstores.query.filter_by(province=province).all()
	# 	result = [{col: getattr(d, col) for col in cols} for d in store]
	# 	if store is None:
	# 		return (jsonify({'message': 'Drugstore does not exist' }), 404)
	# 	return jsonify(store=result)



class DrugstoreAPI(Resource):

	def post(self):
		province = request.form['province'].title()
		cols = ['id','storename','address','province','manager']
		store = Drugstores.query.filter_by(province=province).all()
		result = [{col: getattr(d, col) for col in cols} for d in store]
		if store is None:
			return (jsonify({'message': 'Drugstore does not exist' }), 404)
		return jsonify(store=result)

# 	def get(self):
# 		cols = ['id','storename','address','province','manager']
# 		store = Drugstores.query.filter_by(province=province).all()
# 		result = [{col: getattr(d, col) for col in cols} for d in store]
# 		if store is None:
# 			return (jsonify({'message': 'Drugstore does not exist' }), 404)
# 		return jsonify(store=result)
# 		# return {'storename':store.storename,'address':store.address,'province':store.province,'manager':store.manager,'id':store.id}, 201
		
class DrugsAvailAPI(Resource):

	def get(self,id,page=1):
		store = Drugstores.query.get(id)
		cols = ['id', 'generic', 'brand', 'strength', 'form']
		drug = Drugs.query.paginate(page, 50, True)
		result = [{col: getattr(d, col) for col in cols} for d in drug.items]
		return jsonify(drugs=result)

	# def post(self, id):
	# 	generic = request.form['generic']
	# 	brand = request.form['brand']
	# 	strength = request.form['strength']
	# 	form = request.form['form']

	# 	drugs = Drugs(generic=generic, brand=brand, strength=strength, form=form)
	# 	db.session.add(drugs)
	# 	db.session.commit()
	# 	return {'id':drugs.id, 'generic': drugs.generic, 'brand':drugs.brand, 'strength': drugs.strength, 'form':drugs.form}, 201


api.add_resource(DrugstorePostingAPI, '/FDApp/drugstores', endpoint = 'Drugstores')
api.add_resource(DrugstoreListAPI, '/FDApp/drugstores/<int:page>', endpoint ='drugstores')
api.add_resource(DrugstoreAPI, '/FDApp/drugstore', endpoint='drugstore')
api.add_resource(DrugsAvailAPI, '/FDApp/drugstores/<int:id>/drugs/<int:page>', endpoint ='drugs')


if __name__ == '__main__':
	if not os.path.exists('records.db'):
		db.create_all()
	#app.run(host='0.0.0.0')
	app.run(debug=True)


#-----------
# End of API
#-----------