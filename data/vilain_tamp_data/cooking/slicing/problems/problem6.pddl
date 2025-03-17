(define (problem cooking)
    (:domain cooking)
    (:objects
        a_bot b_bot - Robot
        apple carrot - PhysicalObject
        knife - Tool
        cutting_board bowl tray knife_holder - Location
    )

    (:init
        (Robot b_bot)
        (Robot a_bot)
        (PhysicalObject apple)
        (PhysicalObject carrot)
        (Tool knife)

        (HandEmpty a_bot)
        (HandEmpty b_bot)

        (Location cutting_board)
        (Location tray)
        (Location knife_holder)

        (ToolHolder knife_holder)

        (isWorkspace cutting_board)

        (CanNotReach a_bot knife)
        (CanNotReach b_bot carrot)
        (CanNotReach b_bot apple)

        (At knife knife_holder)
        (At apple tray)
        (At carrot tray)
    )

    (:goal
        (and
            (Served apple bowl)
            (Served carrot bowl)
            (isSliced apple)
            (isSliced carrot)
        )
    )
)
