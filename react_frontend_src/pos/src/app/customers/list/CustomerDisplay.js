import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import validator from 'validator'
import { v4 } from "uuid"


const CustomerDisplay = ({customerID}) => 
    <div>
        { !(customerID) ? null :
        <div className="box box-solid"> 
            <div className="box-body">
                
                    hello world!            
            </div>
        </div>
        }
    </div>


export default CustomerDisplay
