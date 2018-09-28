import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import validator from 'validator'
import { v4 } from "uuid"


const CustomerFormError = ({message}) => 
    <div className="error"> 
        { message }
    </div>


export default CustomerFormError
