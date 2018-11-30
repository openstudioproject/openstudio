import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import validator from 'validator'
import { v4 } from "uuid"

import ButtonCustomerEdit from "../../../components/ui/ButtonCustomerEdit"


class CustomerDisplay extends Component {
    constructor(props) {
        super(props)
        console.log("Customer display props:")
        console.log(props)
    }

    PropTypes = {
        intl: intlShape.isRequired,
        customerID: PropTypes.integer,
        customers: PropTypes.object,
        edit_in_progress: PropTypes.boolean,
        onClickEdit: PropTypes.function
    }

    render() {
        const customerID = this.props.customerID
        const customers = this.props.customers
        const edit_in_progress = this.props.edit_in_progress
        const onClickEdit = this.props.onClickEdit

        return (
            <div>
                { !(customerID) || (edit_in_progress) ? null :
                <div className="box box-solid"> 
                    <div className="box-header">
                        <h3 className="box-title">Customer</h3>
                    </div>
                    <div className="box-body">
                        <div className="col-md-6">
                            <div className="camera-app">
                                <a href="#" id="start-camera" className="visible">Touch here to start the app.</a>
                                <video id="camera-stream"></video>
                                <img id="snap" />

                                <p id="error-message"></p>

                                <div className="controls">
                                <a href="#" id="delete-photo" title="Delete Photo" className="disabled"><i className="material-icons">delete</i></a>
                                    <a href="#" id="take-photo" title="Take Photo"><i className="material-icons">camera_alt</i></a>
                                    <a href="#" id="download-photo" download="selfie.png" title="Save Photo" className="disabled"><i className="material-icons">file_download</i></a>  
                                </div>

                                {/* <!-- Hidden canvas element. Used for taking snapshot of video. --> */}
                                <canvas></canvas>
                            </div>
                        </div>
                        <div className="col-md-6">
                            {customers[customerID].display_name}
                            {customers[customerID].address}
                            <ButtonCustomerEdit onClick={onClickEdit}/>
                        </div>
                    </div>
                </div>
                }
            </div>
        )
    }
}

export default CustomerDisplay


// const CustomerDisplay = ({customerID, customers, edit_in_progress, onClickEdit=f=>f}) => 
//     <div>
//         { !(customerID) || (edit_in_progress) ? null :
//         <div className="box box-solid"> 
//             <div className="box-header">
//                 <h3 className="box-title">Customer</h3>
//             </div>
//             <div className="box-body">
//                 <div className="col-md-6">
//                     <div className="app">
//                         <a href="#" id="start-camera" className="visible">Touch here to start the app.</a>
//                         <video id="camera-stream"></video>
//                         <img id="snap" />

//                         <p id="error-message"></p>

//                         <div className="controls">
//                           <a href="#" id="delete-photo" title="Delete Photo" className="disabled"><i className="material-icons">delete</i></a>
//                             <a href="#" id="take-photo" title="Take Photo"><i className="material-icons">camera_alt</i></a>
//                             <a href="#" id="download-photo" download="selfie.png" title="Save Photo" className="disabled"><i className="material-icons">file_download</i></a>  
//                         </div>

//                         {/* <!-- Hidden canvas element. Used for taking snapshot of video. --> */}
//                         <canvas></canvas>
//                     </div>
//                 </div>
//                 <div className="col-md-6">
//                     {customers[customerID].display_name}
//                     {customers[customerID].address}
//                     <ButtonCustomerEdit onClick={onClickEdit}/>
//                 </div>
//             </div>
//         </div>
//         }
//     </div>


// export default CustomerDisplay
