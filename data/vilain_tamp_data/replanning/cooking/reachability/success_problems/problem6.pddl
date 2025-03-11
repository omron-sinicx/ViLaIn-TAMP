(define (problem slicing)
    (:domain cooking)
    (:objects
        a_bot b_bot - Robot
        potato - PhysicalObject
        knife - Tool
        cutting_board bowl tray plate knife_holder - Location
    )

    (:init
        (Robot b_bot)
        (Robot a_bot)
        (PhysicalObject potato)
        (Tool knife)

        (HandEmpty a_bot)
        (HandEmpty b_bot)

        (Location cutting_board)
        (Location bowl)
        (Location tray)
        (Location plate)
        (Location knife_holder)

        (ToolHolder knife_holder)

        (isWorkspace cutting_board)

        (CanNotReach a_bot knife)
        (CanNotReach b_bot potato)

        (At knife knife_holder)
        (At potato tray)
    )

    (:goal
        (and
            (isSliced potato)
            (Served potato bowl)
        )
    )
)
