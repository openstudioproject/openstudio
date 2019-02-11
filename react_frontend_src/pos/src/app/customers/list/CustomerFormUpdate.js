import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import validator from 'validator'
import { v4 } from "uuid"
import Inputmask from "inputmask"

import CustomerFormError from "./CustomerFormError"




class CustomerFormUpdate extends Component {
    constructor(props) {
        super(props)
        console.log(props)
        this.inputDateOfBirth = React.createRef();
    }

    PropTypes = {
        intl: intlShape.isRequired,
    }

    componentDidUpdate() {
        if (this.props.display) {
            {Inputmask({"placeholder": this.props.inputmask_date}).mask(this.inputDateOfBirth.current)}
        }
    }


    render() {
        const customers = this.props.customers
        const customerID = this.props.customerID
        const inputmask_date = this.props.inputmask_date
        const display = this.props.display
        const error_data = this.props.error_data
        const onSubmit = this.props.onSubmit
        const onCancel = this.props.onCancel        

        return (
            !(display) ? null :
                <div className="box box-solid"> 
                    <div className="box-header">
                        <h3 className="box-title">Edit customer</h3>
                        <button className="btn btn-default pull-right"
                                onClick={onCancel}>
                            Cancel
                        </button>
                    </div>
                    <div className="box-body">
                        <form onSubmit={onSubmit}>
                        <label htmlFor="first_name">First Name</label>
                        <input 
                            id="first_name" 
                            className="form-control"
                            name="first_name" 
                            type="text" 
                            defaultValue={ customers[customerID].first_name }
                        />
                        <CustomerFormError message={ (error_data.first_name) ? error_data.first_name : "" } />
                        <label htmlFor="last_name">Last Name</label>
                        <input 
                            id="last_name" 
                            className="form-control"
                            name="last_name" 
                            type="text" 
                            defaultValue={ customers[customerID].last_name }
                        />
                        <CustomerFormError message={ (error_data.last_name) ? error_data.last_name : "" } />
                        <label htmlFor="email">Email</label>
                        <input 
                            id="email" 
                            className="form-control"
                            name="email" 
                            type="text"
                            defaultValue={ customers[customerID].email} 
                        />
                        <CustomerFormError message={ (error_data.email) ? error_data.email : "" } />
                            <label htmlFor="email">Mobile</label>
                            <input 
                                id="mobile" 
                                className="form-control"
                                name="mobile" 
                                type="text" 
                                defaultValue={ customers[customerID].mobile }
                            />
                            <CustomerFormError message={ (error_data.mobile) ? error_data.mobile : "" } />
                            <label htmlFor="email">Date of birth</label>
                            <input 
                                id="date_of_birth" 
                                className="form-control date-inputmask"
                                autoComplete="off"
                                name="date_of_birth" 
                                type="text" 
                                defaultValue={ customers[customerID].date_of_birth }
                                data-inputmask={"'alias': 'datetime', 'inputFormat': '" + inputmask_date + "'"}
                                data-mask="true"
                                ref={this.inputDateOfBirth}
                            />
                            <CustomerFormError message={ (error_data.date_of_birth) ? error_data.date_of_birth : "" } />
                            <br />
                            <button className="btn btn-primary">Save</button>
                        </form>
                    </div>
                </div>
        )
    }
}

export default CustomerFormUpdate

// const CustomerFormUpdate = ({display, customerID, customers, error_data={}, onSubmit=f=>f, onCancel=f=>f}) => 
//     <div>
//         { !(display) ? null :
//         <div className="box box-solid"> 
//             <div className="box-header">
//                 <h3 className="box-title">Edit customer</h3>
//                 <button onClick={onCancel}
//                         className="btn btn-default pull-right">
//                     Cancel
//                 </button>
//             </div>
//             <div className="box-body">
//                 <form onSubmit={onSubmit}>
//                     <label htmlFor="first_name">First Name</label>
//                     <input 
//                         id="first_name" 
//                         className="form-control"
//                         name="first_name" 
//                         type="text" 
//                         defaultValue={ customers[customerID].first_name }
//                     />
//                     <CustomerFormError message={ (error_data.first_name) ? error_data.first_name : "" } />
//                     <label htmlFor="last_name">Last Name</label>
//                     <input 
//                         id="last_name" 
//                         className="form-control"
//                         name="last_name" 
//                         type="text" 
//                         defaultValue={ customers[customerID].last_name }
//                     />
//                     <CustomerFormError message={ (error_data.last_name) ? error_data.last_name : "" } />
//                     <label htmlFor="email">Email</label>
//                     <input 
//                         id="email" 
//                         className="form-control"
//                         name="email" 
//                         type="text"
//                         defaultValue={ customers[customerID].email} 
//                     />
//                     <CustomerFormError message={ (error_data.email) ? error_data.email : "" } />
//                     <label htmlFor="email">Mobile</label>
//                     <input 
//                         id="mobile" 
//                         className="form-control"
//                         name="mobile" 
//                         type="text" 
//                     />
//                     <CustomerFormError message={ (error_data.mobile) ? error_data.mobile : "" } />
//                     <label htmlFor="email">Date of birth</label>
//                     <input 
//                         id="date_of_birth" 
//                         className="form-control date-inputmask"
//                         autoComplete="off"
//                         name="date_of_birth" 
//                         type="text" 
//                         data-inputmask={"'alias': 'datetime', 'inputFormat': '" + date_format + "'"}
//                         data-mask="true"
//                         ref={this.inputDateOfBirth}
//                     />
//                     <CustomerFormError message={ (error_data.date_of_birth) ? error_data.date_of_birth : "" } />
//                     <br />
//                     <button className="btn btn-primary">Save</button>
//                 </form>
//             </div>
//         </div>
//         }
//     </div>


// export default CustomerFormUpdate
