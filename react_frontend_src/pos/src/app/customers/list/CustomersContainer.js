import { connect } from 'react-redux'
import { injectIntl } from 'react-intl';
import { withRouter } from 'react-router'

import Customers from './Customers'
import { appOperations } from '../../duck'
import { customersListOperations } from './duck'


const mapStateToProps = state => 
    ({
        app: state.app,
        barcode_scans: state.app.settings.data.customers_barcodes,
        customers: state.customers.list,
        memberships: state.customers.memberships
    })

const mapDispatchToProps = dispatch =>
    ({
        setPageTitle(title) {
            dispatch(appOperations.setPageTitle(title))
        },
        createCustomer(data) {
            dispatch(customersListOperations.createCustomer(data))
        },
        setCreateCustomerStatus(status) {
            dispatch(customersListOperations.setCreateCustomerStatus(status))
        },
        setUpdateCustomerStatus(status) {
            dispatch(customersListOperations.setUpdateCustomerStatus(status))
        },
        clearSearchTimeout() {
            dispatch(customersListOperations.clearSearchTimeout())
        },
        clearDisplayCustomerID() {
            dispatch(customersListOperations.clearDisplayCustomerID())
        },
        setDisplayCustomerID(id) {
            dispatch(customersListOperations.setDisplayCustomerID(id))
        },
        setSearchTimeout(timeout) {
            dispatch(customersListOperations.setSearchTimeout(timeout))
        },
        clearSearchCustomerID() {
            dispatch(customersListOperations.clearSearchCustomerID())
        },
        setSearchCustomerID(id) {
            dispatch(customersListOperations.setSearchCustomerID(id))
        },
        clearSearchValue() {
            dispatch(customersListOperations.clearSearchValue())
        },
        setSearchValue(value) {
            dispatch(customersListOperations.setSearchValue(value))
        },
        clearSelectedCustomerID() {
            dispatch(customersListOperations.clearSelectedCustomerID())
        },
        setSelectedCustomerID(id) {
            dispatch(customersListOperations.setSelectedCustomerID(id))
        }
    })


const CustomersContainer = withRouter(injectIntl(connect(
    mapStateToProps,
    mapDispatchToProps
)(Customers)))

export default CustomersContainer