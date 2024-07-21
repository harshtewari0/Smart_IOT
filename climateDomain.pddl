(define (domain climate)
    (:requirements :strips :typing :negative-preconditions)
    
    (:types
        temp - object
        hum - object
        sensor - object
    )
    
    (:predicates
        ; Temperature predicates
        (isTempHigh ?temp - temp)
        (isTempLow ?temp - temp)
        (isTempSensHigh ?sensor - sensor)
        (isTempSensLow ?sensor - sensor)
        (off_fan ?sensor - sensor)
        (on_fan ?sensor - sensor)
        
        ; Humidity predicates
        (isHumHigh ?hum - hum)
        (isHumLow ?hum - hum)
        (isHumSensHigh ?sensor - sensor)
        (isHumSensLow ?sensor - sensor)
        (off_humidifier ?sensor - sensor)
        (on_humidifier ?sensor - sensor)
    )
    
    (:action SwitchOFFFan
        :parameters (?temp - temp ?sensor - sensor)
        :precondition (and (isTempHigh ?temp) (isTempSensHigh ?sensor))
        :effect (off_fan ?sensor)
    )
    
    (:action SwitchONFan
        :parameters (?temp - temp ?sensor - sensor)
        :precondition (and (isTempLow ?temp) (isTempSensLow ?sensor))
        :effect (on_fan ?sensor)
    )

    (:action SwitchOFFHumidifier
        :parameters (?hum - hum ?sensor - sensor)
        :precondition (and (isHumHigh ?hum) (isHumSensHigh ?sensor))
        :effect (off_humidifier ?sensor)
    )
    
    (:action SwitchONHumidifier
        :parameters (?hum - hum ?sensor - sensor)
        :precondition (and (isHumLow ?hum) (isHumSensLow ?sensor))
        :effect (on_humidifier ?sensor)
    )
)

