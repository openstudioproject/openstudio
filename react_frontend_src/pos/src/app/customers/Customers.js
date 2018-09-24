import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import { NavLink } from 'react-router-dom'
import validator from 'validator'


import PageTemplate from "../../components/PageTemplate"
import InputGroupSearch from "../../components/ui/InputGroupSearch"
import ButtonBack from "../../components/ui/ButtonBack"


class Customers extends Component {
    constructor(props) {
        super(props)
        console.log("Customers props:")
        console.log(props)
    }

    PropTypes = {
        intl: intlShape.isRequired,
        setPageTitle: PropTypes.function,
        app: PropTypes.object,
        state: PropTypes.object,
    }

    componentWillMount() {
        this.props.setPageTitle(
            this.props.intl.formatMessage({ id: 'app.pos.customers.page_title' })
        )
    }

    componentDidMount() {

    }

    setSearchValue(value) {
        console.log('done something :)!')
        console.log(value)
    }

    onChange(e) {
        const value = e.target.value
        const customers = this.props.customers
        console.log("timeout: " + customers.searchTimeout)
        if ( customers.searchTimeout ) {
            this.props.clearSearchTimeout()
            console.log('reset timeout')
        }

        let timeout
        this.props.setSearchTimeout(
            setTimeout(() => this.setSearchValue(value), 
                (validator.isInt(value)) ? timeout = 225 : timeout = 750)
        )
    }


    onClickButtonBack(e) {
        console.log("clicked")
        this.props.history.push('/products/school/classcards')
    }

    render() {
        const customers = this.props.customers
        const intl = this.props.intl

        return (
            <PageTemplate app_state={this.props.app}>
                { 
                    (!customers.loaded) ? 
                        <div>{intl.formatMessage({ id: 'app.pos.customers.loading_message' })}</div> :
                        <section className="customers_main">
                            {/* <div className="pull-right">
                                <NavLink to={"/checkin/revenue/" + this.props.match.params.clsID}>
                                    {this.props.intl.formatMessage({ id: "app.pos.checkin.attendane.verify_teacher_payment"})}
                                </NavLink>
                            </div> */}
                            <ButtonBack onClick={this.onClickButtonBack.bind(this)}>
                                Cancel
                            </ButtonBack>
                            <InputGroupSearch placeholder={this.props.intl.formatMessage({ id: 'app.general.placeholders.search' })}
                                              onChange={this.onChange.bind(this)} /> <br />
                            {/* <AttendanceList attendance_items={this.props.attendance.data} /> */}
                        </section>
                }
            </PageTemplate>
        )
    }
}

export default Customers
