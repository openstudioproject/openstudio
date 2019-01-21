import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import validator from 'validator'
import { v4 } from "uuid"
import Inputmask from "inputmask"
// import Inputmask from "inputmask/dist/inputmask/inputmask.date.extensions";

import CustomerFormError from "./CustomerFormError"




class CustomerFormCreate extends Component {
    constructor(props) {
        super(props)
        console.log(props)
        this.inputDateOfBirth = React.createRef();
    }

    PropTypes = {
        intl: intlShape.isRequired,
    }

    componentWillMount() {
    }

    componentDidMount() {
        Inputmask({"placeholder": this.props.date_format}).mask(this.inputDateOfBirth.current)
        // this.inputDateOfBirth.current.inputmask(this.props.date_format, { 'placeholder': this.props.date_format })
    }


    render() {
        // const date_format = this.props.date_format
        const date_format = this.props.date_format
        const error_data = this.props.error_data
        const onSubmit = this.props.onSubmit
        const onCancel = this.props.onCancel        

        return (
            <div className="box box-solid"> 
                <div className="box-header">
                    <h3 className="box-title">Add customer</h3>
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
                        />
                        <CustomerFormError message={ (error_data.first_name) ? error_data.first_name : "" } />
                        <label htmlFor="last_name">Last Name</label>
                        <input 
                            id="last_name" 
                            className="form-control"
                            name="last_name" 
                            type="text" 
                        />
                        <CustomerFormError message={ (error_data.last_name) ? error_data.last_name : "" } />
                        <label htmlFor="email">Email</label>
                        <input 
                            id="email" 
                            className="form-control"
                            name="email" 
                            type="text" 
                        />
                        <CustomerFormError message={ (error_data.email) ? error_data.email : "" } />
                        <label htmlFor="email">Mobile</label>
                        <input 
                            id="mobile" 
                            className="form-control"
                            name="mobile" 
                            type="text" 
                        />
                        <CustomerFormError message={ (error_data.mobile) ? error_data.mobile : "" } />
                        <label htmlFor="email">Date of birth</label>
                        <input 
                            id="date_of_birth" 
                            className="form-control date-inputmask"
                            autoComplete="off"
                            name="date_of_birth" 
                            type="text" 
                            data-inputmask={"'alias': 'datetime', 'inputFormat': '" + date_format + "'"}
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

export default CustomerFormCreate



// const CustomerFormCreate = ({date_format="yyyy-mm-dd", error_data={}, onSubmit=f=>f, onCancel=f=>f}) => 
//     <div className="box box-solid"> 
//         <div className="box-header">
//             <h3 className="box-title">Add customer</h3>
//             <button className="btn btn-default pull-right"
//                     onClick={onCancel}>
//                 Cancel
//             </button>
//         </div>
//         <div className="box-body">
//             <form onSubmit={onSubmit}>
//                 <label htmlFor="first_name">First Name</label>
//                 <input 
//                     id="first_name" 
//                     className="form-control"
//                     name="first_name" 
//                     type="text" 
//                 />
//                 <CustomerFormError message={ (error_data.first_name) ? error_data.first_name : "" } />
//                 <label htmlFor="last_name">Last Name</label>
//                 <input 
//                     id="last_name" 
//                     className="form-control"
//                     name="last_name" 
//                     type="text" 
//                 />
//                 <CustomerFormError message={ (error_data.last_name) ? error_data.last_name : "" } />
//                 <label htmlFor="email">Email</label>
//                 <input 
//                     id="email" 
//                     className="form-control"
//                     name="email" 
//                     type="text" 
//                 />
//                 <CustomerFormError message={ (error_data.email) ? error_data.email : "" } />
//                 <label htmlFor="email">Mobile</label>
//                 <input 
//                     id="mobile" 
//                     className="form-control"
//                     name="mobile" 
//                     type="text" 
//                 />
//                 <CustomerFormError message={ (error_data.mobile) ? error_data.mobile : "" } />
//                 <label htmlFor="email">Date of birth</label>
//                 <input 
//                     id="date_of_birth" 
//                     className="form-control date-inputmask"
//                     autoComplete="off"
//                     name="date_of_birth" 
//                     type="text" 
//                     date-inputmask="'alias': 'dd-mm-yyyy'"
//                     data-mask="true"
//                 />
//                 <CustomerFormError message={ (error_data.date_of_birth) ? error_data.date_of_birth : "" } />
//                 <br />
//                 <button className="btn btn-primary">Save</button>
//             </form>
//         </div>
//     </div>


// export default CustomerFormCreate
