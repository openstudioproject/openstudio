import T from './types'
import { appReducer } from './reducers'
import deepFreeze from 'deep-freeze'

describe("app Reducer", () => {
    it("SET_ERROR success", () => {
        const state = {}
        const action = {
            type: T.SET_ERROR,
            error: true
        }

        deepFreeze(state)
        deepFreeze(action)
        const results = appReducer(state, action)
        expect(results)
            .toEqual({
                error: true
            })
    })

    // it("SET_ERROR_MESSAGE success")
    })