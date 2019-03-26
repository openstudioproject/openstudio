import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import { withRouter } from 'react-router'
import { NavLink } from 'react-router-dom'
import { Formik, Form, Field, ErrorMessage } from 'formik'

import ExpensesTemplate from "./ExpensesTemplateContainer"
import FormError from "./FormError"

class ExpenseAdd extends Component {
    constructor(props) {
        super(props)
        console.log("Expense Add props:")
        console.log(props)
    }

    PropTypes = {
        intl: intlShape.isRequired,
        app: PropTypes.object,
    }

    render() {
        const history = this.props.history
        const error_data = this.props.error_data || {}
        const return_url = '/expenses'

        return (
            <ExpensesTemplate app={this.props.app} expenses={this.props.expenses} setPageTitle={this.props.setPageTitle}>
                <div className="box box-solid">
                    <div className='box-header'>
                        <h3 className="box-title">Add expense</h3>
                    </div>
                    <form onSubmit={() => this.props.onSubmit}>
                        <div className="box-body">
                            <label htmlFor="amount">Amount</label>
                            <input 
                                id="amount" 
                                className="form-control"
                                name="amount" 
                                type="text" 
                            />
                            <FormError message={ (error_data.amount) ? error_data.amount : "" } />
                        </div>
                        <div className="box-footer">
                            <button className="btn btn-primary"
                                    type="submit">
                                Save
                            </button>
                            <button className="btn btn-link"
                                    type="button"
                                    onClick={() => history.push(return_url)}>
                                Cancel
                            </button>
                        </div>
                    </form>
                </div>
            </ExpensesTemplate>
        )
    }
}

export default withRouter(ExpenseAdd)



// import React, { Component } from "react"
// import { intlShape } from "react-intl"
// import PropTypes from "prop-types"
// import validator from 'validator'
// import { v4 } from "uuid"
// import Inputmask from "inputmask"
// // import Inputmask from "inputmask/dist/inputmask/inputmask.date.extensions";

// import CustomerFormError from "./CustomerFormError"




// class CustomerFormCreate extends Component {
//     constructor(props) {
//         super(props)
//         console.log(props)
//         this.inputDateOfBirth = React.createRef();
//     }

//     PropTypes = {
//         intl: intlShape.isRequired,
//     }

//     componentWillMount() {
//     }

//     componentDidMount() {
//         Inputmask({"placeholder": this.props.inputmask_date}).mask(this.inputDateOfBirth.current)
//         // this.inputDateOfBirth.current.inputmask(this.props.inputmask_date, { 'placeholder': this.props.inputmask_date })
//     }


//     render() {
//         // const inputmask_date = this.props.inputmask_date
//         const inputmask_date = this.props.inputmask_date
//         const error_data = this.props.error_data
//         const onSubmit = this.props.onSubmit
//         const onCancel = this.props.onCancel        

//         return (
//             <div className="box box-solid"> 
//                 <div className="box-header">
//                     <h3 className="box-title">Add customer</h3>
//                     <button className="btn btn-default pull-right"
//                             onClick={onCancel}>
//                         Cancel
//                     </button>
//                 </div>
//                 <div className="box-body">
//                     <form onSubmit={onSubmit}>
//                         <label htmlFor="first_name">First Name</label>
//                         <input 
//                             id="first_name" 
//                             className="form-control"
//                             name="first_name" 
//                             type="text" 
//                         />
//                         <CustomerFormError message={ (error_data.first_name) ? error_data.first_name : "" } />
//                         <label htmlFor="last_name">Last Name</label>
//                         <input 
//                             id="last_name" 
//                             className="form-control"
//                             name="last_name" 
//                             type="text" 
//                         />
//                         <CustomerFormError message={ (error_data.last_name) ? error_data.last_name : "" } />
//                         <label htmlFor="email">Email</label>
//                         <input 
//                             id="email" 
//                             className="form-control"
//                             name="email" 
//                             type="text" 
//                         />
//                         <CustomerFormError message={ (error_data.email) ? error_data.email : "" } />
//                         <label htmlFor="email">Mobile</label>
//                         <input 
//                             id="mobile" 
//                             className="form-control"
//                             name="mobile" 
//                             type="text" 
//                         />
//                         <CustomerFormError message={ (error_data.mobile) ? error_data.mobile : "" } />
//                         <label htmlFor="email">Date of birth</label>
//                         <input 
//                             id="date_of_birth" 
//                             className="form-control date-inputmask"
//                             autoComplete="off"
//                             name="date_of_birth" 
//                             type="text" 
//                             data-inputmask={"'alias': 'datetime', 'inputFormat': '" + inputmask_date + "'"}
//                             data-mask="true"
//                             ref={this.inputDateOfBirth}
//                         />
//                         <CustomerFormError message={ (error_data.date_of_birth) ? error_data.date_of_birth : "" } />
//                         <br />
//                         <button className="btn btn-primary">Save</button>
//                     </form>
//                 </div>
//             </div>
//         )
//     }
// }

// export default CustomerFormCreate

