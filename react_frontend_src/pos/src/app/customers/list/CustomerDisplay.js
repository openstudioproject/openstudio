import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import validator from 'validator'
import { v4 } from "uuid"

import ButtonCustomerEdit from "../../../components/ui/ButtonCustomerEdit"

const CustomerDisplay = ({customerID, customers, edit_in_progress, onClickEdit=f=>f}) => 
    <div>
        { !(customerID) || (edit_in_progress) ? null :
        <div className="box box-solid"> 
            <div className="box-header">
                <h3 className="box-title">Customer</h3>
            </div>
            <div className="box-body">
                {customers[customerID].display_name}
                {customers[customerID].address}
                <ButtonCustomerEdit onClick={onClickEdit}/>
            </div>
        </div>
        }
    </div>


export default CustomerDisplay
