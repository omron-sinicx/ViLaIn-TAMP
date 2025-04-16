(define (problem cooking)
    (:domain cooking)
    (:objects
        a_bot b_bot - Robot
        apple - PhysicalObject
        knife - Tool
        cutting_board tray plate knife_holder - Location
    )

    (:init
        (Robot b_bot)
        (Robot a_bot)
        (PhysicalObject apple)
        (Tool knife)

        (HandEmpty a_bot)
        (HandEmpty b_bot)

        (Location cutting_board)
        (Location tray)
        (Location plate)
        (Location knife_holder)

        (ToolHolder knife_holder)

        (isWorkspace cutting_board)

        (At knife knife_holder)
        (At apple tray)
    )

    (:goal
        (and
            (At apple cutting_board)
        )
    )
)
