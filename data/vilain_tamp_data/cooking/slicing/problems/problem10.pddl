(define (problem cooking)
    (:domain cooking)
    (:objects
        a_bot b_bot - Robot
        cucumber apple - PhysicalObject
        knife - Tool
        cutting_board bowl tray knife_holder - Location
    )

    (:init
        (Robot b_bot)
        (Robot a_bot)
        (PhysicalObject cucumber)
        (PhysicalObject apple)
        (Tool knife)

        (HandEmpty a_bot)
        (HandEmpty b_bot)

        (Location cutting_board)
        (Location tray)
        (Location knife_holder)
        (Location bowl)

        (ToolHolder knife_holder)

        (isWorkspace cutting_board)

        (CanNotReach a_bot knife knife_holder)
        (CanNotReach b_bot cucumber tray)
        (CanNotReach b_bot apple tray)

        (At knife knife_holder)
        (At cucumber tray)
        (At apple tray)
    )

    (:goal
        (and
            (Served cucumber bowl)
            (Served apple bowl)
            (isSliced cucumber)
            (isSliced apple)
        )
    )
)
