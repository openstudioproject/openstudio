import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import validator from 'validator'
import { v4 } from "uuid"


const CustomerFormCreate = ({onSubmit=f=>f}) => 
    <div className="box box-solid"> 
        <div className="box-header">
            <h3 className="box-title">Add customer</h3>
        </div>
        <div className="box-body">
            <form onSubmit={onSubmit}>
                <label htmlFor="first_name">First Name</label>
                <input 
                    id="first_name" 
                    name="first_name" 
                    type="text" 
                />
                <label htmlFor="last_name">Last Name</label>
                <input 
                    id="last_name" 
                    name="last_name" 
                    type="text" 
                />
                <label htmlFor="email">Email</label>
                <input 
                    id="email" 
                    name="email" 
                    type="text" 
                />

                <button>Save</button>
            </form>
        </div>
    </div>


export default CustomerFormCreate
