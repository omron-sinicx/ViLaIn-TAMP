(define (problem slicing)
    (:domain cooking)
    (:objects
        a_bot b_bot - Robot
        carrot - PhysicalObject
        knife - Tool
        cutting_board tray plate knife_holder - Location
    )

    (:init
        (Robot b_bot)
        (Robot a_bot)
        (PhysicalObject carrot)
        (Tool knife)

        (HandEmpty a_bot)
        (HandEmpty b_bot)

        (Location cutting_board)
        (Location tray)
        (Location plate)
        (Location knife_holder)
        (Location other_plate)

        (ToolHolder knife_holder)

        (isWorkspace cutting_board)

        (CanNotReach a_bot knife)
        (CanNotReach b_bot carrot)

        (At knife knife_holder)
        (At carrot tray)
        (At tomato cutting_board)
    )

    (:goal
        (and
            (isSliced carrot)
        )
    )
)
