(define (problem cooking)
    (:domain cooking)
    (:objects
        a_bot b_bot - Robot
        potato carrot - PhysicalObject
        knife - Tool
        cutting_board bowl tray plate knife_holder - Location
    )

    (:init
        (Robot b_bot)
        (Robot a_bot)
        (PhysicalObject potato)
        (PhysicalObject carrot)
        (Tool knife)

        (HandEmpty a_bot)
        (HandEmpty b_bot)

        (Location cutting_board)
        (Location tray)
        (Location plate)
        (Location knife_holder)

        (ToolHolder knife_holder)

        (isWorkspace cutting_board)

        (CanNotReach a_bot knife)
        (CanNotReach b_bot carrot)
        (CanNotReach b_bot potato)

        (At knife knife_holder)
        (At potato tray)
        (At carrot tray)
    )

    (:goal
        (and
            (Served potato bowl)
            (Served carrot bowl)
            (isSliced potato)
            (isSliced carrot)
        )
    )
)
