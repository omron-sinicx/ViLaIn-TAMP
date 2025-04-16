(define (problem pick_and_place)
    (:domain cooking)
    (:objects
        a_bot b_bot - Robot
        cucumber apple - PhysicalObject
        knife - Tool
        cutting_board tray plate plate2 knife_holder - Location
    )

    (:init
        (Robot a_bot)
        (PhysicalObject cucumber)
        (PhysicalObject apple)
        (Tool knife)

        (HandEmpty a_bot)

        (Location cutting_board)
        (Location tray)
        (Location plate)
        (Location plate2)
        (Location knife_holder)

        (ToolHolder knife_holder)

        (isWorkspace cutting_board)


        (At knife knife_holder)
        (At cucumber plate)
        (At apple plate2)

        (isNotFree plate)
        (isNotFree plate2)
        (isNotFree tray)
        (isNotFree knife_holder)
    )

    (:goal
        (and
            (At cucumber plate2)
            (At apple plate)
        )
    )
)
