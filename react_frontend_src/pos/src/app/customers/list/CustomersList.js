import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import validator from 'validator'
import { v4 } from "uuid"


const CustomersList = ({customers}) => 
    <div className="box box-solid"> 
        <div className="box-header">
            <h3 className="box-title">Search results</h3>
        </div>
        <div className="box-body">
            { !(customers.length) ? "Search to list customers" :
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
            }
        </div>
    </div>


export default CustomersList
