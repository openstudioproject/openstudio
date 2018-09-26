import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import validator from 'validator'
import { v4 } from "uuid"


import CustomersListItem from "./CustomersListItem"

const CustomersList = ({customers}) => 
    <div className="box box-default"> 
        <div className="box-body">
            <table className="table table-striped table-hover">
            <thead>
                <tr>
                    <th></th>
                    <th>Customer</th>
                    <th>Address</th>
                </tr>
            </thead>
            <tbody>
                {customers.map((customer, i) => 
                    <tr key={v4()}>
                        <td><img src={customer.thumbsmall}></img></td>
                        <td>{customer.display_name}</td>
                        <td>{customer.address}</td>
                    </tr>
                )}
            </tbody>
            </table>
        </div>
    </div>


export default CustomersList
