import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import validator from 'validator'
import { v4 } from "uuid"


const CustomerFormUpdate = ({display, customerID, customers, onSubmit=f=>f}) => 
    <div>
        { !(display) ? null :
        <div className="box box-solid"> 
            <div className="box-header">
                <h3 className="box-title">Edit customer</h3>
            </div>
            <div className="box-body">
                <form onSubmit={onSubmit}>
                    <label htmlFor="first_name">First Name</label>
                    <input 
                        id="first_name" 
                        name="first_name" 
                        type="text" 
                        defaultValue={ customers[customerID].first_name }
                    />
                    <label htmlFor="last_name">Last Name</label>
                    <input 
                        id="last_name" 
                        name="last_name" 
                        type="text" 
                        defaultValue={ customers[customerID].last_name }
                    />
                    <label htmlFor="email">Email</label>
                    <input 
                        id="email" 
                        name="email" 
                        type="text"
                        defaultValue={ customers[customerID].last_name} 
                    />
                    <button>Save</button>
                </form>
            </div>
        </div>
        }
    </div>


export default CustomerFormUpdate
