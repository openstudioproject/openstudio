import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import validator from 'validator'
import { v4 } from "uuid"


import CustomersListItem from "./CustomersListItem"

const CustomersList = ({customers}) => 
    <div className="box box-default"> 
        <div className="box-body">
            {customers.map((customer, i) => 
                <div key={v4()}>
                    {customer.first_name}
                </div>
                // <AttendanceListItem key={"ai_" + v4()}
                //                     data={ai} />
            )}
        </div>
    </div>


export default CustomersList


// class CustomersList extends Component {
//     constructor(props) {
//         super(props)
//         console.log("Customers props:")
//         console.log(props)
//     }

//     PropTypes = {
//         intl: intlShape.isRequired,
//         customers: PropTypes.object,
//     }

//     componentWillMount() {
//     }

//     componentDidMount() {
//     }

//     // onChange(e) {
//     //     const value = e.target.value
//     //     const customers = this.props.customers
//     //     console.log("timeout: " + customers.searchTimeout)
//     //     if ( customers.searchTimeout ) {
//     //         this.props.clearSearchTimeout()
//     //         console.log('reset timeout')
//     //     }

//     //     let timeout
//     //     this.props.setSearchTimeout(
//     //         setTimeout(() => this.setSearchValue(value), 
//     //             (validator.isInt(value)) ? timeout = 225 : timeout = 750)
//     //     )
//     // }


//     // onClickButtonBack(e) {
//     //     console.log("clicked")
//     //     this.props.history.push('/products/school/classcards')
//     // }

//     render() {
//         const customers = this.props.customers
//         const intl = this.props.intl

//         let customers_display = []
//         if ( customers.searchID ) {
//             customers_display = [
//                 customers.data[customers.searchID]
//             ]
//         }
//         "Customers display"
//         console.log(customers_display)

//         return (  
//             customers_display.map((customer, i) => {
//                 console.log(customer)
//                 { <div>{customer.last_name}</div> }
//             })              
//             // <section>
//             //     List here<br/>
//             //     SearchID: {' '}
//             //     {customers.searchID}
//             //     <br />
//             //     SelectedID: {' '}
//             //     {customers.selectedID}
//             //     <br />
//             //     {
//             //         customers_display.map((customer, i) => {
//             //             <div>{customer.customers_display}</div>
                        
//             //             // console.log(i)
//             //             //console.log(customer)
//             //             // <CustomersListItem key={"customer_" + v4()} 
//             //             //                    data={customer} />
//             //         })
//             //     }
                

//             // </section>
//         )
//     }
// }

// export default CustomersList
