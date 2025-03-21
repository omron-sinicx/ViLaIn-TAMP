(define (problem pick_and_place)
    (:domain cooking)
    (:objects
        a_bot b_bot - Robot
        cucumber apple - PhysicalObject
        knife - Tool
        cutting_board tray plate knife_holder - Location
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
        (Location knife_holder)

        (ToolHolder knife_holder)

        (isWorkspace cutting_board)

        (CanNotReach a_bot knife)

        (At knife knife_holder)
        (At cucumber tray)
        (At apple plate)
    )

    (:goal
        (and
            (At cucumber plate)
            (At apple tray)
        )
    )
)
