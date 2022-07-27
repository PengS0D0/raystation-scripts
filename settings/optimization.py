# encoding: utf8

# Import local files:
import region_codes as RC

# Optimization parameters class - for setting up an optimization in RayStation.
class Optimization(object):

  def __init__(self,
    max_number_of_iterations=40,
    optimality_tolerance=0.000001,
    compute_final_dose=True,
    compute_intermediate_dose=False,
    iterations_in_preparations_phase=7,
    final_arc_gantry_spacing=4,
    max_arc_delivery_time=90,
    max_leaf_travel_distance_per_degree=0,
    use_max_leaf_travel_distance_per_degree=False,
    use_sliding_window_sequencing=False
  ):
    self.max_number_of_iterations = max_number_of_iterations
    self.optimality_tolerance = optimality_tolerance
    self.compute_final_dose = compute_final_dose
    self.compute_intermediate_dose = compute_intermediate_dose
    self.iterations_in_preparations_phase = iterations_in_preparations_phase
    self.final_arc_gantry_spacing = final_arc_gantry_spacing
    self.max_arc_delivery_time = max_arc_delivery_time
    self.max_leaf_travel_distance_per_degree = max_leaf_travel_distance_per_degree
    self.use_max_leaf_travel_distance_per_degree = use_max_leaf_travel_distance_per_degree
    self.use_sliding_window_sequencing = use_sliding_window_sequencing
    self.max_arc_mu = None
  
  # Applies the parameters of this Optimization object to a RayStation PlanOptimization object.
  def apply_to(self, plan_optimization):
    plan_optimization.OptimizationParameters.Algorithm.MaxNumberOfIterations = self.max_number_of_iterations
    plan_optimization.OptimizationParameters.Algorithm.OptimalityTolerance = self.optimality_tolerance
    plan_optimization.OptimizationParameters.DoseCalculation.ComputeFinalDose = self.compute_final_dose
    plan_optimization.OptimizationParameters.DoseCalculation.ComputeIntermediateDose = self.compute_intermediate_dose
    plan_optimization.OptimizationParameters.DoseCalculation.IterationsInPreparationsPhase = self.iterations_in_preparations_phase
    plan_optimization.OptimizationParameters.TreatmentSetupSettings[0].BeamSettings[0].ArcConversionPropertiesPerBeam.FinalArcGantrySpacing = self.final_arc_gantry_spacing
    plan_optimization.OptimizationParameters.TreatmentSetupSettings[0].BeamSettings[0].ArcConversionPropertiesPerBeam.MaxArcDeliveryTime = self.max_arc_delivery_time
    plan_optimization.OptimizationParameters.TreatmentSetupSettings[0].BeamSettings[0].ArcConversionPropertiesPerBeam.MaxArcMU = self.max_arc_mu
    plan_optimization.OptimizationParameters.TreatmentSetupSettings[0].SegmentConversion.ArcConversionProperties.MaxLeafTravelDistancePerDegree = self.max_leaf_travel_distance_per_degree
    plan_optimization.OptimizationParameters.TreatmentSetupSettings[0].SegmentConversion.ArcConversionProperties.UseMaxLeafTravelDistancePerDegree = self.use_max_leaf_travel_distance_per_degree
    plan_optimization.OptimizationParameters.TreatmentSetupSettings[0].SegmentConversion.ArcConversionProperties.UseSlidingWindowSequencing = self.use_sliding_window_sequencing
    
  # Set the max arc mu parameter:
  def set_max_arc_mu(self, mu):
    self.max_arc_mu = mu


# Categories of optimization settings:
default = Optimization()
sliding_window = Optimization(final_arc_gantry_spacing=2, max_arc_delivery_time=120, use_sliding_window_sequencing=True)
sbrt = Optimization(final_arc_gantry_spacing=2, max_arc_delivery_time=150, max_leaf_travel_distance_per_degree=0.3, use_max_leaf_travel_distance_per_degree=True, use_sliding_window_sequencing=True)


# Set up optimization parameters, based on region code (i.e. treatment site) and fraction dose (i.e. fractionated treatment or SBRT).
# FIXME: Would be more robust to use the prescription object here, instead of the fraction_dose (for interpreting sbrt/conventional treatment).
def optimization_parameters(region_code, fraction_dose):
  # Set default optimization settings:
  opt = default
  # Assign optimization settings based on region code (and in some cases fraction dose):
  if region_code in RC.brain_partial_codes:
    # Partial brain:
    if fraction_dose > 6:
      # Stereotactic brain
      opt = sbrt
    else:
      # Partial brain (ordinary fractionation):
      opt = sliding_window
  elif region_code in RC.breast_codes:
    # Partial breast/Whole breast/Regional breast:
    opt = sliding_window
  elif region_code in RC.lung_and_mediastinum_codes:
    # Lung:
    if fraction_dose > 9:
      # Stereotactic lung:
      opt = sbrt
    elif fraction_dose == 7:
      # Stereotactic lung: (7Gy * 8fx)
      opt = sbrt
    else:
      # Conventional lung:
      opt = sliding_window
  elif region_code in RC.prostate_codes:
    # Prostate:
    if region_code in RC.prostate_node_codes:
      # Prostate (or prostate bed) with lymph nodes:
      opt = sliding_window
  elif region_code in RC.rectum_codes:
    # Rectum:
    opt = sliding_window
  elif region_code in RC.palliative_codes:
    # Palliative treatment:
    if fraction_dose > 8:
      # Stereotactic palliative:
      opt = sbrt
    elif fraction_dose >= 6 and fraction_dose <= 7:
      # Stereotactic palliative: (6-7Gy * 5fx)
      opt = sbrt
    else:
      # Conventional palliative:
      if region_code in RC.whole_pelvis_codes:
        opt = sliding_window
  # Set max number of monitor units (for all non-sbrt optimizations):
  if opt != sbrt:
    opt.set_max_arc_mu(fraction_dose * 250)
  # Return the assigned optimization settings:
  return opt
