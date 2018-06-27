import React from 'react'
import { connect } from 'react-redux'

import { Welcome } from "./Pages"
import { setLoaderStatus, setLoaderMessage } from "../actions";

console.log('app here')
const mapStateToProps = state => 
    ({
        loader: state.loader
    })

const mapDispatchToProps = dispatch =>
    ({
        setLoaderStatus(status) {
            dispatch(setLoaderStatus(status))
        },
        setLoaderMessage(message) {
            dispatch(setLoaderMessage(message))
        }
    })

export const App = connect(
    mapStateToProps,
    mapDispatchToProps
)(Welcome)