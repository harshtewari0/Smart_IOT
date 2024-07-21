
(define (problem ClimateProblem)
    (:domain climate)

    (:objects
        temp_high temp_low temp_ambient - temp
        hum_high hum_low hum_ambient - hum
        f_high f_low f_none - sensor
        h_high h_low h_none - sensor
    )

    (:init
        ; Temperature initial state
        (isTempHigh temp_high)
        (isTempSensHigh f_high)
        (isTempLow temp_high)
        (isTempSensLow f_high)

        ; Humidity initial state
        (isHumHigh hum_high)
        (isHumSensHigh h_high)
        (isHumLow hum_high)
        (isHumSensLow h_high)
    )

    (:goal
        (and
            (off_fan f_high)
            (off_humidifier h_high)
        )
    )
)
        