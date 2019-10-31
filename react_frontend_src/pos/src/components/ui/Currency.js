import React from "react"
import { connect } from 'react-redux'


const Currency = ({settings, amount}) =>
    <span>
        {settings.currency_symbol} { ' ' }
        {amount}
    </span>


const mapStateToProps = state => 
    ({
        settings: state.app.settings.data
    })

const ConnectedCurrency = connect(
    mapStateToProps
)(Currency)

export default ConnectedCurrency