(define (problem pick_and_place)
    (:domain cooking)
    (:objects
        a_bot b_bot - Robot
        carrot cucumber - PhysicalObject
        knife - Tool
        cutting_board tray plate knife_holder - Location
    )

    (:init
        (Robot a_bot)
        (Robot b_bot)
        (PhysicalObject carrot)
        (PhysicalObject cucumber)
        (Tool knife)

        (HandEmpty a_bot)

        (Location cutting_board)
        (Location tray)
        (Location plate)
        (Location knife_holder)

        (ToolHolder knife_holder)

        (isWorkspace cutting_board)

        (At knife knife_holder)
        (At carrot tray)
        (At cucumber cutting_board)
    )

    (:goal
        (and
            (At carrot cutting_board)
            (At cucumber tray)
        )
    )
)
