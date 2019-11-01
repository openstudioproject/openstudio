import React from "react"
import { connect } from 'react-redux'


const Currency = ({settings, amount}) =>
    <span>
        {settings.currency_symbol} { ' ' }
        {parseFloat(amount).toFixed(2)}
    </span>


const mapStateToProps = state => 
    ({
        settings: state.app.settings.data
    })

const ConnectedCurrency = connect(
    mapStateToProps
)(Currency)

export default ConnectedCurrency